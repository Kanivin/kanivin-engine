# Copyright (c) 2015, Kanivin Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import re

from bs4 import BeautifulSoup

import kanivin
from kanivin.custom.doctype.customize_form.customize_form import reset_customization
from kanivin.tests.utils import KanivinTestCase
from kanivin.utils import random_string, set_request
from kanivin.website.doctype.blog_post.blog_post import get_blog_list
from kanivin.website.serve import get_response
from kanivin.website.utils import clear_website_cache
from kanivin.website.website_generator import WebsiteGenerator

test_dependencies = ["Blog Post"]


class TestBlogPost(KanivinTestCase):
	def setUp(self):
		reset_customization("Blog Post")

	def tearDown(self):
		if hasattr(kanivin.local, "request"):
			delattr(kanivin.local, "request")

	def test_generator_view(self):
		pages = kanivin.get_all(
			"Blog Post", fields=["name", "route"], filters={"published": 1, "route": ("!=", "")}, limit=1
		)

		set_request(path=pages[0].route)
		response = get_response()

		self.assertTrue(response.status_code, 200)

		html = response.get_data().decode()
		self.assertTrue(
			'<article class="blog-content" itemscope itemtype="http://schema.org/BlogPosting">' in html
		)

	def test_generator_not_found(self):
		pages = kanivin.get_all("Blog Post", fields=["name", "route"], filters={"published": 0}, limit=1)

		route = f"test-route-{kanivin.generate_hash(length=5)}"

		kanivin.db.set_value("Blog Post", pages[0].name, "route", route)

		set_request(path=route)
		response = get_response()

		self.assertTrue(response.status_code, 404)

	def test_category_link(self):
		# Make a temporary Blog Post (and a Blog Category)
		blog = make_test_blog("Test Category Link")

		# Visit the blog post page
		set_request(path=blog.route)
		blog_page_response = get_response()
		blog_page_html = kanivin.safe_decode(blog_page_response.get_data())

		# On blog post page find link to the category page
		soup = BeautifulSoup(blog_page_html, "html.parser")
		category_page_link = next(iter(soup.find_all("a", href=re.compile(blog.blog_category))))
		category_page_url = category_page_link["href"]

		cached_value = kanivin.db.value_cache.get(("DocType", "Blog Post", "name"))
		kanivin.db.value_cache[("DocType", "Blog Post", "name")] = (("Blog Post",),)

		# Visit the category page (by following the link found in above stage)
		set_request(path=category_page_url)
		category_page_response = get_response()
		category_page_html = kanivin.safe_decode(category_page_response.get_data())
		# Category page should contain the blog post title
		self.assertIn(blog.title, category_page_html)

		# Cleanup
		kanivin.db.value_cache[("DocType", "Blog Post", "name")] = cached_value
		kanivin.delete_doc("Blog Post", blog.name)
		kanivin.delete_doc("Blog Category", blog.blog_category)

	def test_blog_pagination(self):
		# Create some Blog Posts for a Blog Category
		category_title, blogs, BLOG_COUNT = "List Category", [], 4

		for _ in range(BLOG_COUNT):
			blog = make_test_blog(category_title)
			blogs.append(blog)

		filters = kanivin._dict({"blog_category": scrub(category_title)})
		# Assert that get_blog_list returns results as expected

		self.assertEqual(len(get_blog_list(None, None, filters, 0, 3)), 3)
		self.assertEqual(len(get_blog_list(None, None, filters, 0, BLOG_COUNT)), BLOG_COUNT)
		self.assertEqual(len(get_blog_list(None, None, filters, 0, 2)), 2)
		self.assertEqual(len(get_blog_list(None, None, filters, 2, BLOG_COUNT)), 2)

		# Cleanup Blog Post and linked Blog Category
		for blog in blogs:
			kanivin.delete_doc(blog.doctype, blog.name)
		kanivin.delete_doc("Blog Category", blogs[0].blog_category)

	def test_caching(self):
		# to enable caching
		kanivin.flags.force_website_cache = True
		print(kanivin.session.user)

		clear_website_cache()
		# first response no-cache
		pages = kanivin.get_all(
			"Blog Post",
			fields=["name", "route"],
			filters={"published": 1, "title": "_Test Blog Post"},
			limit=1,
		)

		route = pages[0].route
		set_request(path=route)
		# response = get_response()
		response = get_response()
		# TODO: enable this assert
		# self.assertIn(('X-From-Cache', 'False'), list(response.headers))

		set_request(path=route)
		response = get_response()
		self.assertIn(("X-From-Cache", "True"), list(response.headers))

		kanivin.flags.force_website_cache = True

	def test_spam_comments(self):
		# Make a temporary Blog Post (and a Blog Category)
		blog = make_test_blog("Test Spam Comment")

		# Create a spam comment
		kanivin.get_doc(
			doctype="Comment",
			comment_type="Comment",
			reference_doctype="Blog Post",
			reference_name=blog.name,
			comment_email='<a href="https://example.com/spam/">spam</a>',
			comment_by='<a href="https://example.com/spam/">spam</a>',
			published=1,
			content='More spam content. <a href="https://example.com/spam/">spam</a> with link.',
		).insert()

		# Visit the blog post page
		set_request(path=blog.route)
		blog_page_response = get_response()
		blog_page_html = kanivin.safe_decode(blog_page_response.get_data())

		self.assertNotIn('<a href="https://example.com/spam/">spam</a>', blog_page_html)
		self.assertIn("More spam content. spam with link.", blog_page_html)

		# Cleanup
		kanivin.delete_doc("Blog Post", blog.name)
		kanivin.delete_doc("Blog Category", blog.blog_category)

	def test_like_dislike(self):
		test_blog = make_test_blog()

		kanivin.db.delete("Comment", {"comment_type": "Like", "reference_doctype": "Blog Post"})

		from kanivin.templates.includes.likes.likes import like

		liked = like("Blog Post", test_blog.name, True)
		self.assertEqual(liked, True)

		disliked = like("Blog Post", test_blog.name, False)
		self.assertEqual(disliked, False)

		kanivin.db.delete("Comment", {"comment_type": "Like", "reference_doctype": "Blog Post"})
		test_blog.delete()


def scrub(text):
	return WebsiteGenerator.scrub(None, text)


def make_test_blog(category_title="Test Blog Category"):
	category_name = scrub(category_title)
	if not kanivin.db.exists("Blog Category", category_name):
		kanivin.get_doc(dict(doctype="Blog Category", title=category_title)).insert()
	if not kanivin.db.exists("Blogger", "test-blogger"):
		kanivin.get_doc(dict(doctype="Blogger", short_name="test-blogger", full_name="Test Blogger")).insert()

	return kanivin.get_doc(
		dict(
			doctype="Blog Post",
			blog_category=category_name,
			blogger="test-blogger",
			title=random_string(20),
			route=random_string(20),
			content=random_string(20),
			published=1,
		)
	).insert()
