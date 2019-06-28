# -*- coding: utf-8 -*-
import os
import json
import scrapy


class MainSpider(scrapy.Spider):
    name = 'main'
    allowed_domains = ['mbasic.facebook.com']
    base_url = "https://mbasic.facebook.com"
    start_urls = [
        f"{base_url}/login.php?next=https%3A%2F%2Fmbasic.facebook.com%2Fucllove"
    ]

    def parse_post(self, response):
        post_text = ""
        hashtags = []
        for para in response.css("#root > #m_story_permalink_view p"):
            text = para.css("p::text").get()
            if text is None:  # assume is hashtag
                hashtags.append(dict(
                    text="".join(para.css("span::text").getall()),
                    url=para.css("a").attrib.get('href')
                ))
                continue
            post_text += text
        yield(dict(
            hashtags=hashtags,
            text=post_text,
            url=response.meta['url'],
            timestamp=response.meta['timestamp']
        ))

    def build_post_url(self, post_meta):
        return f"https://mbasic.facebook.com/story.php?story_fbid={post_meta['mf_story_key']}&id={post_meta['page_id']}"

    def get_post_timestamp(self, post_meta):
        return list(post_meta['page_insights'].values())[0]['post_context']['publish_time']

    def parse_page(self, response):
        for post in response.xpath("//div[starts-with(@id, 'u_0_')]"):
            post_meta = post.attrib.get('data-ft')
            if post_meta is None:
                continue
            post_meta = json.loads(post_meta)
            yield response.follow(
                url=self.build_post_url(post_meta),
                callback=self.parse_post,
                meta=dict(
                    url=self.build_post_url(post_meta),
                    timestamp=self.get_post_timestamp(post_meta)
                )
            )
        next_page_url = response.css(
            "#structured_composer_async_container .h a::attr(href)").get()
        yield response.follow(
            url=f"{MainSpider.base_url}{next_page_url}",
            callback=self.parse_page
        )

    def parse(self, response):
        email = os.getenv("FACEBOOK_EMAIL")
        password = os.getenv("FACEBOOK_PASSWORD")
        formdata = {
            "pass": password,
            "email": email,
        }
        return scrapy.FormRequest.from_response(response,
                                                formid="login_form",
                                                formdata=formdata,
                                                callback=self.parse_page)
