# -*- coding: utf-8 -*-

# -- stdlib --
import random

# -- third party --
# -- own --
from gamepack.thb import characters
from gamepack.thb.actions import ttags
from gamepack.thb.ui.ui_meta.common import card_desc, gen_metafunc, my_turn, passive_clickable
from gamepack.thb.ui.ui_meta.common import passive_is_action_valid

# -- code --
__metaclass__ = gen_metafunc(characters.sanae)


class Sanae:
    # Character
    char_name = u'东风谷早苗'
    port_image = 'thb-portrait-sanae'
    miss_sound_effect = 'thb-cv-sanae_miss'
    description = (
        u'|DB常识满满的现人神 东风谷早苗 体力：3|r\n\n'
        u'|G奇迹|r：你可以弃置一张与本回合已弃置过的牌类型均不同的牌，然后摸一张牌。若你以此法弃置了3张牌，你可以令一名角色回复一点体力。\n\n'
        u'|G信仰|r：出牌阶段限一次，你可以令至多两名其他角色各交给你一张手牌，然后你交给其各一张牌。\n\n'
        u'|G神裔|r：当你成为群体符卡的目标后，你可以摸一张牌并跳过此次结算。\n\n'
        u'|DB（画师：Pixiv ID 37694260，CV：VV）|r'
    )


class Miracle:
    name = u'奇迹'

    def clickable(g):
        return my_turn()

    def effect_string(act):
        return u'|G【%s】|r发动了|G奇迹|r，弃置了%s' % (
            act.target.ui_meta.char_name,
            card_desc(act.card.associated_cards[0]),
        )

    def is_action_valid(g, cl, tl):
        cards = cl[0].associated_cards
        if not cards:
            return (False, u'请选择一张牌')

        c = cards[0]

        me = g.me
        if set(c.category) & ttags(me).setdefault('miracle_categories', set()):
            return (False, u'你已经弃置过相同类型的牌')

        return (True, u'奇迹是存在的！')

    def sound_effect(act):
        return 'thb-cv-sanae_miracle'


class MiracleAction:

    def target(pl):
        if not pl:
            return (False, u'奇迹：请选择1名受伤的玩家，回复一点体力（否则不发动）')

        return (True, u'奇迹：回复1点体力')


class SanaeFaith:
    name = u'信仰'

    def clickable(g):
        return my_turn() and not ttags(g.me)['faith']

    def effect_string(act):
        return u'|G【%s】|r的|G信仰|r大作战！向%s收集了信仰！' % (
            act.source.ui_meta.char_name,
            u'、'.join([u'|G【%s】|r' % p.ui_meta.char_name for p in act.target_list]),
        )

    def is_action_valid(g, cl, tl):
        cards = cl[0].associated_cards
        if cards:
            return (False, u'请不要选择牌！')

        return (True, u'团队需要信仰！')

    def sound_effect(act):
        return 'thb-cv-sanae_faith'


class SanaeFaithCollectCardAction:
    # choose_card meta
    def choose_card_text(g, act, cards):
        if act.cond(cards):
            return (True, u'信仰：交出这一张手牌，然后收回一张牌')
        else:
            return (False, u'信仰：请交出一张手牌')


class SanaeFaithReturnCardAction:
    # choose_card meta
    def choose_card_text(g, act, cards):
        if act.cond(cards):
            return (True, u'信仰：将这一张牌返还给%s' % act.target.ui_meta.char_name)
        else:
            return (False, u'信仰：选择一张牌返还给%s' % act.target.ui_meta.char_name)


class GodDescendant:
    name = u'神裔'
    clickable = passive_clickable
    is_action_valid = passive_is_action_valid


class GodDescendantHandler:
    # choose_option
    choose_option_buttons = ((u'发动', True), (u'不发动', False))
    choose_option_prompt = u'你要发动【神裔】吗？'


class GodDescendantSkipAction:

    def effect_string(act):
        return u'|G【%s】|r发动了|G神裔|r，跳过了结算并摸一张牌。' % (
            act.target.ui_meta.char_name,
        )

    def sound_effect(act):
        return 'thb-cv-sanae_goddescendant%d' % random.choice([1, 2])
