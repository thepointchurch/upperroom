import urllib.parse

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed, Enclosure, Rss201rev2Feed

from .models import Resource, ResourceFeed
from ..utils.storages.attachment import attachment_url


class MaybePodcastFeed(Rss201rev2Feed):
    def rss_attributes(self):
        attrs = super(MaybePodcastFeed, self).rss_attributes()
        if self.feed['is_podcast']:
            attrs['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
            attrs['version'] = '2.0'
        return attrs

    def add_root_elements(self, handler):
        super(MaybePodcastFeed, self).add_root_elements(handler)
        if self.feed['is_podcast']:
            if self.feed['subtitle']:
                handler.addQuickElement('itunes:subtitle', self.feed['subtitle'])
            if self.feed['author_name']:
                handler.addQuickElement('itunes:author', self.feed['author_name'])
            handler.addQuickElement('itunes:summary', self.feed['description'])
            if self.feed['categories']:
                handler.startElement("itunes:category", {'text': self.feed['categories'][0]})
                for category in self.feed['categories'][1:]:
                    handler.addQuickElement('itunes:category', attrs={'text': category})
                handler.endElement("itunes:category")
            handler.addQuickElement('itunes:explicit', 'no')
            handler.startElement("itunes:owner", {})
            handler.addQuickElement('itunes:email',
                                    self.feed['owner_email'] if 'owner_email' in self.feed
                                    else settings.WEBMASTER_EMAIL)
            if 'owner_name' in self.feed:
                handler.addQuickElement('itunes:name', self.feed['owner_name'])
            handler.endElement("itunes:owner")

            # This is ugly but it lets us default to a standard image among the static files
            if 'image_url' in self.feed:
                image_url = self.feed['image_url']
            else:
                image_url = 'style/podcast.png'
            try:
                if '.' in settings.STATICFILES_BUCKET:
                    bucket = settings.STATICFILES_BUCKET
                else:
                    bucket = settings.STATICFILES_BUCKET + '.s3.amazonaws.com'
                static_root = urllib.parse.urljoin(self.feed['feed_url'], '//' + bucket + '/')
            except AttributeError:
                static_root = urllib.parse.urljoin(self.feed['feed_url'], settings.STATIC_URL)
            handler.addQuickElement('itunes:image',
                                    attrs={'href': urllib.parse.urljoin(static_root, image_url)})

    def add_item_elements(self, handler, item):
        super(MaybePodcastFeed, self).add_item_elements(handler, item)
        if self.feed['is_podcast']:
            handler.addQuickElement(u'itunes:title', item['title'])
            handler.addQuickElement(u'itunes:summary', item['description'])
            handler.addQuickElement(u'itunes:episodeType', 'full')
            if 'author' in item:
                handler.addQuickElement(u'itunes:author', item['author'])
            if 'duration' in item:
                handler.addQuickElement(u'itunes:duration', item['duration'])


class ResourceFeedRSS(Feed):
    feed_type = MaybePodcastFeed

    def feed_extra_kwargs(self, obj):
        args = {
            'is_podcast': obj.is_podcast,
        }
        if obj.owner_name:
            args['owner_name'] = obj.owner_name
        if obj.owner_email:
            args['owner_email'] = obj.owner_email
        image_url = obj.image_url
        if image_url:
            args['image_url'] = self.request.build_absolute_uri(image_url)
        return args

    def item_extra_kwargs(self, item):
        args = {}
        if item.author:
            args['author'] = item.author.fullname
        attachment = item.attachments.filter(mime_type__in=self.object.mime_types).first()
        if attachment and attachment.metadata and 'length' in attachment.metadata:
            args['duration'] = attachment.metadata['length']
        return args

    def get_object(self, request, slug):
        self.object = get_object_or_404(ResourceFeed, slug=slug)
        self.request = request
        return self.object

    def title(self, obj):
        return obj.title

    def link(self, obj):
        return reverse('resources:tag', kwargs={'slug': obj.slug})

    def description(self, obj):
        return obj.description

    def author_name(self, obj):
        return obj.owner_name

    def categories(self, obj):
        return obj.categories

    def feed_copyright(self, obj):
        return obj.copyright

    def items(self, obj):
        resources = Resource.published_objects.filter(is_private=False).\
                                               filter(parent__isnull=True).\
                                               filter(tags__in=obj.tags.all())
        if obj.mime_type_list:
            resources = resources.filter(attachments__mime_type__in=obj.mime_types)
        return resources.order_by('-published')[:10]

    def item_author_name(self, item):
        if item.author:
            return item.author.fullname

    def item_pubdate(self, item):
        return item.published

    def item_updateddate(self, item):
        return item.modified

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_categories(self, item):
        return [tag.name for tag in item.tags.difference(self.object.tags.all())]

    def item_enclosures(self, item):
        enc = []
        for attachment in item.attachments.filter(mime_type__in=self.object.mime_types):
            url = attachment_url(reverse('resources:attachment', kwargs={'pk': attachment.id}),
                                 attachment.file.name,
                                 True, self.request)
            enc.append(Enclosure(url=url,
                                 length=str(attachment.size),
                                 mime_type=attachment.mime_type))
            # Limit podcasts to only one enclosure
            if self.object.is_podcast:
                break
        return enc


class ResourceFeedAtom(ResourceFeedRSS):
    feed_type = Atom1Feed
    subtitle = ResourceFeedRSS.description

    def link(self, obj):
        return reverse('resources:atom', kwargs={'slug': obj.slug})
