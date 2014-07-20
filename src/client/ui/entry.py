# -*- coding: utf-8 -*-
import sys
import os

from utils import hook

import gevent

import logging
log = logging.getLogger('UI_Entry')


def start_ui():
    # ATI workarounds
    import pyglet
    from pyglet import gl

    @hook(gl)
    def glDrawArrays(ori, *a, **k):
        from pyglet.gl import glBegin, glEnd, GL_QUADS
        glBegin(GL_QUADS)
        glEnd()
        return ori(*a, **k)

    # ---------------

    from client.ui.base import init_gui, ui_message

    init_gui()

    # This forces all game resources to initialize,
    # else they will be imported firstly by GameManager,
    # then resources will be loaded at a different thread,
    # resulting white planes.
    # UPDATE: no more threading now, but retain notice above.
    from client.ui.resource import resource
    import gamepack
    gamepack.init_ui_resources()

    from client.ui.resloader import Resource
    Resource.load_resources()

    from client.ui.base.baseclasses import main_window
    main_window.set_icon(resource.icon)
    main_window.set_visible(True)

    # custom errcheck
    import pyglet.gl.lib as gllib

    import ctypes

    def my_errcheck(result, func, arguments):
        from pyglet import gl
        error = gl.glGetError()
        if error and error != 1286:
            # HACK: The 1286(INVALID_FRAMEBUFFER_OPERATION) error again!
            # This time I DIDN'T EVEN USE FBO! ATI!!
            msg = ctypes.cast(gl.gluErrorString(error), ctypes.c_char_p).value
            raise gl.GLException((error, msg))
        return result

    gllib.errcheck = my_errcheck
    # ------------------------------------

    from screens import UpdateScreen, ServerSelectScreen
    from client.ui.controls import ConfirmBox
    from client.core import Executive
    from options import options

    us = UpdateScreen()
    us.switch()
    sss = ServerSelectScreen()

    errmsgs = {
        'update_disabled': u'自动更新已被禁止',
        'error': u'更新过程出现错误，您可能无法正常进行游戏！',
    }

    @gevent.spawn
    def do_update():
        msg = Executive.update(us.update_message)

        if msg == 'up2date':
            sss.switch()
        elif msg == 'update_disabled' and options.fastjoin:
            @gevent.spawn
            def func():
                from client.ui.soundmgr import SoundManager
                SoundManager.mute()
                gevent.sleep(0.3)
                sss.switch()
                gevent.sleep(0.3)
                Executive.connect_server(('127.0.0.1', 9999), ui_message)
                gevent.sleep(0.3)
                Executive.auth('Proton1', 'abcde')
                gevent.sleep(0.3)
                Executive.quick_start_game('THBattle')
                gevent.sleep(0.3)
                Executive.get_ready()

        elif msg in errmsgs:
            b = ConfirmBox(errmsgs[msg], parent=us)

            @b.event
            def on_confirm(val):
                sss.switch()
        else:
            os.execv(sys.executable, [sys.executable] + sys.argv)

    # workaround for pyglet's bug
    if sys.platform == 'win32':
        import pyglet.app.win32
        pyglet.app.win32.Win32EventLoop._next_idle_time = None

    pyglet.app.run()
