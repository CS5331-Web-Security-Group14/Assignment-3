import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from targetItems import *
from pipelines import *
import json
from scrapy import signals
import urlparse
import logging


class ScrapeTarget(CrawlSpider):
	name = "scrapeTarget"
	start_urls = [
		'http://ec2-13-250-106-60.ap-southeast-1.compute.amazonaws.com:8080/'
	]
	allowed_domains =[
		'ec2-13-250-106-60.ap-southeast-1.compute.amazonaws.com', ''
	]
	injection_points = {}
	logging.basicConfig(filename='scanner_logs.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
	logging.info('Starting Phase 1: Crawling\n')
	
	def parse(self, response):
		#extract forms on the page
		forms = response.css('form')
		parsedResponseURL = urlparse.urlparse(response.url)
		urlKey = parsedResponseURL.scheme+"://"+ parsedResponseURL.netloc
		if urlKey not in self.injection_points:
			self.injection_points[urlKey] = []
		for form in forms:
		    formJson = {}
		    formname = form.xpath('@action').extract()
		    if(len(formname)>0):
			formname = formname[0]
		    else:
			formname = parsedResponseURL.path
		    formJson['endpoint'] = formname
		    method = form.xpath('@method').extract()
		    formJson['method'] = method[0] if len(method)>0 else 'GET'
		    formJson['params'] = []
		    inputs = form.css('input')
		    for inp in inputs:
			name = inp.xpath('@name').extract()
			typ = inp.xpath('@type').extract()
			value = inp.xpath('@value').extract()
			inpJson = {'name': name[0] if len(name)>0 else '', 'type': typ[0] if len(typ)>0 else 'text', 'value': value[0] if len(value) > 0 else ''}
			formJson['params'].append(inpJson)
		    if formJson not in self.injection_points[urlKey]:
		    	self.injection_points[urlKey].append(formJson)
		
		links = response.css('a::attr(href)').extract()
		for link in links:
			parsedUrl = urlparse.urlparse(link)
			if parsedUrl.netloc in self.allowed_domains:
				if parsedUrl.query != '':
					getJson = {'method' : 'GET', 'params': [], 'endpoint': urlparse.urljoin(parsedResponseURL.path,parsedUrl.path)}
					for key in urlparse.parse_qs(parsedUrl.query):
						getJson['params'].append({'name':key})
					if getJson not in self.injection_points[urlKey]:
						self.injection_points[urlKey].append(getJson)
				yield scrapy.http.Request(url=response.urljoin(link), callback=self.parse)
				
			

	@classmethod
	def from_crawler(cls, crawler, *args, **kwargs):
		spider = super(ScrapeTarget, cls).from_crawler(crawler, *args, **kwargs)
		crawler.signals.connect(spider.spider_opened, signals.spider_opened)
		crawler.signals.connect(spider.spider_closed, signals.spider_closed)
		return spider

	def spider_opened(self, spider):
        	logging.info('Opening {} spider'.format(spider.name))

	def spider_closed(self, spider):
		logging.info('\n\nCrawling completed. Generating endpoints file')
		logging.info('\n\nPhase 1: Crawling completed\n\n---------------------\n\n')
        	with open(self.name + '_phase1.json', 'w') as fp:
            		json.dump(self.injection_points, fp, sort_keys=True, indent=4)
