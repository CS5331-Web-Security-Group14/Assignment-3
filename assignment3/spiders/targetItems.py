import scrapy

class URLItem(scrapy.Item):
	from_url = scrapy.Field()
	to_url = scrapy.Field()

class FormItem(scrapy.Item):
	form_id = scrapy.Field()
	form_name = scrapy.Field()
	form_method = scrapy.Field()
	form_action = scrapy.Field()
	form_url = scrapy.Field()

class InputItem(scrapy.Item):
	input_form = scrapy.Field()
	input_id = scrapy.Field()
	input_name = scrapy.Field()
	input_type = scrapy.Field()
	input_value = scrapy.Field()
