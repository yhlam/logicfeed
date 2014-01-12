from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context
from django.contrib import auth

from datetime import datetime
from email.mime.image import MIMEImage
from itertools import takewhile
import base64
import random

import fbconsole
import premailer

from .models import Feed, Image, Font, LastUpdate, LogicFeedConfig


User = auth.get_user_model()


def to_feed(post):
    _, id_str = post['id'].split('_')
    feed_id = int(id_str)
    text = post['message']
    created_time_str = post['created_time']
    created_time = datetime.strptime(created_time_str, '%Y-%m-%dT%H:%M:%S%z')
    feed, _ = Feed.objects.get_or_create(id=feed_id, text=text, created_time=created_time)
    return feed


def get_fb_data(url):
    """The iterator to the json responses of the given url

    :param url: URL requested
    :return: iterator to the responses
    """
    config = LogicFeedConfig.objects.get()
    fbconsole.AUTH_SCOPE = ['read_stream']
    fbconsole.authenticate_via_cookie(config.fb_cookies_c_user, config.fb_cookies_xs)
    return fbconsole.iter_pages(fbconsole.get(url))


def get_feeds(user_id, since):
    """Get all feeds of the given user since a specific time

    :param user_id: facebook user id
    :param since: lower bound of created time of Feed queried
    :return: a list of Feed queried
    :rtype: list
    """

    def is_created_after(feed):
        return feed.created_time > since

    def has_message(post):
        return 'message' in post

    url = '/{}/posts'.format(user_id)
    return list(takewhile(is_created_after,
                          map(to_feed,
                              filter(has_message, get_fb_data(url)))))


def pull_new_feeds():
    """Process the new feeds since last update

    Pull all new feeds since last update and update the last update timestamp.
    Notify the staff with meme generated randomly for the new feeds through email.
    """
    config = LogicFeedConfig.objects.get()
    last_update = LastUpdate.objects.get_timestamp_and_update()
    feeds = get_feeds(config.src_user_id, last_update)

    staff = User.objects.filter(is_staff=True)
    staff_emails = map(lambda user: user.email, staff)
    for feed in feeds:
        meme = generate_random_meme(feed)
        send_email(feed, meme, staff_emails)


def rand_model(model_type):
    """Get a aandom model of the given type

    :param model_type: model type to be selected random
    :return: random model
    """
    all_models = model_type.objects.all()
    model = random.choice(all_models)
    return model


def generate_random_meme(feed):
    """Generate a meme with random background image and font for the feed

    :param feed:
    :return: bytes of the generated meme
    :rtype: bytes
    """
    image = rand_model(Image)
    font = rand_model(Font)
    return feed.generate_meme(image, fill_color='white', border_color='black',
                              border_size=1, font_path=font.path)


def send_email(feed, meme_bytes, recipients):
    """Send email to the given recipients to notify them the new feed

    :param feed: new feed to notify
    :param meme_bytes: bytes of meme
    :param recipients: list of recipient email
    """
    config = LogicFeedConfig.objects.get()
    with open(config.avatar.path, 'rb') as f:
        avatar_bytes = f.read()
        avatar = MIMEImage(avatar_bytes)
        avatar.add_header('Content-Id', '<avatar>')
    meme = MIMEImage(meme_bytes)
    meme.add_header('Content-Id', '<meme>')
    plain = render_plain_email(config.src_user_name, config.dst_user_name,
                               feed.text, feed.id)
    html = render_html_email(config.src_user_name, config.dst_user_name,
                             feed.text, feed.id)
    email = EmailMultiAlternatives(config.email_subject, plain,
                                   config.email_sender, recipients)
    email.attach_alternative(html, 'text/html')
    email.attach(avatar)
    email.attach(meme)
    email.send()


def encode_image(bytes, type):
    """Encode bytes of image into data string for HTML

    :param bytes: bytes of the image
    :param type: type of the image
    :return: data string of the bytes
    :rtype: str
    """
    return 'data:image/{};base64,{}'.format(type, base64.b64encode(bytes).decode('ascii'))


def render_plain_email(src_user_name, dst_user_name, message, feed_id):
    """Render the plain text notification email

    :param src_user_name: feed source user name
    :param dst_user_name: user name of the destination
    :param message: message of the feed
    :param feed_id: feed ID
    :return: plain text email content of notification
    :rtype: str
    """
    template = loader.get_template('email.txt')
    content = template.render(Context({
        'src_user_name': src_user_name,
        'dst_user_name': dst_user_name,
        'message': message,
        'feed_id': feed_id
    }))
    return content


def render_html_email(src_user_name, dst_user_name, message, feed_id):
    """Render the HTML notification email

    :param src_user_name: feed source user name
    :param dst_user_name: user name of the destination
    :param message: message of the feed
    :param feed_id: feed ID
    :return: HTML email content of notification
    :rtype: str
    """
    template = loader.get_template('email.html')
    content = template.render(Context({
        'src_user_name': src_user_name,
        'dst_user_name': dst_user_name,
        'message': message,
        'feed_id': feed_id
    }))
    compressed_content = premailer.transform(content)
    return compressed_content
