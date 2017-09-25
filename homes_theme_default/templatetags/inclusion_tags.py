from django import template

from homes.models import Block, SEO, Branch, Banner

register = template.Library()

@register.inclusion_tag('templatetags/header.html')
def page_header(title):
    return {
        'title': title
    }


@register.inclusion_tag('templatetags/block.html', takes_context=True)
def page_block(context, slug):
    block = Block.objects.filter(slug=slug, status=Block.STATUS_CHOICE_ACTIVE).first()
    return {
        'slug': slug,
        'block':block,
        'request': context['request']
    }


@register.inclusion_tag('templatetags/banner.html')
def page_banner(slug):
    banner = Banner.objects.filter(slug=slug, status=Banner.STATUS_CHOICE_ACTIVE).first()
    return {
        'slug': slug,
        'banner':banner,
    }


@register.inclusion_tag('templatetags/toolbar.html', takes_context=True)
def page_toolbar(context):
    return {
        'instance': SEO.objects.filter(url=context['request'].path).first(),
        'request': context['request']
    }


@register.inclusion_tag('templatetags/meta.html', takes_context=True)
def page_meta(context):
    return{
        'instance': SEO.objects.filter(url=context['request'].path).first(),
        'request': context['request']
    }


@register.inclusion_tag('templatetags/branches.html')
def branch_list():
    return {
        'branches': Branch.active.all()
    }