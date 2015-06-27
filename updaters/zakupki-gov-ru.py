from tenders.models import *


class Runner:


	name = 'Обновление с сайта государственных закупок России'
	alias = 'zakupki-gov-ru'
	urls = {
		'base':     'ftp.zakupki.gov.ru',
		'essences': 'fcs_nsi',
		'regions':  'fcs_regions',
		'country':  'nsiOKSM',
		'currency': 'nsiCurrency',
		'okei':     'nsiOKEI',
		'kosgu':    'nsiKOSGU',
		'okopf':    'nsiOKOPF',
		'okpd':     'nsiOKPD',
		'oktmo':    'nsiOKTMO'}


	def __init__(self):

		# Загрузчик
		self.updater = Updater.objects.take(
			alias = self.alias,
			name  = self.name)


	def run(self):

		# Проверяем наличие параметров авторизации
		if not self.updater.login or not self.updater.password:
			print('Ошибка: Проверьте параметры авторизации. Кажется их нет.')
			return False


		# Обновляем справочники
#		self.getEssencesList()                                                  # Тест

		self.updateEssence('country')
		self.updateRegions()
		self.updateEssence('currency')
		self.updateEssence('okei')
		self.updateEssence('kosgu')
		self.updateEssence('okopf')
		self.updateEssence('okpd')
		self.updateEssence('oktmo')



		# Обновляем планы регионов
		# TODO

		# Обновляем тендеры регионов
		# TODO

		return True


	def getFTPCatalog(self, catalog = None):
		'Возвращает содержимое папки'

		# Импортируем
		from ftplib import FTP

		# Авторизуемся
		ftp = FTP(host = self.urls['base'])
		ftp.login(user = self.updater.login, passwd = self.updater.password)

		# Переходим в нужный каталог
		if catalog:
			ftp.cwd(catalog)

		# Получаем содержимое каталога
		result = ftp.nlst()

		# Закрываем соединение
		ftp.close()

		# Возвращаем результат
		return result


	def getZipFromFTP(self, file_name, catalog = None):
		'Скачивает и возвращает файл с FTP-сервера'

		# Импортируем
		from ftplib import FTP
		from io import BytesIO
		from zipfile import ZipFile

		# Инициализируем переменные
		ftp = FTP(host = self.urls['base'])
		zip_file = BytesIO(b"")

		# Авторизуемся
		ftp.login(user = self.updater.login, passwd = self.updater.password)

		# Переходим в нужный каталог
		if catalog:
			ftp.cwd(catalog)

		# Скачиваем файл
		ftp.retrbinary("RETR {}".format(file_name), zip_file.write)
		zip_data  = ZipFile(zip_file)

		# Возвращаем результат
		return zip_data


	def getEssencesList(self):
		'Получает список сущностей для тестирования'

		essences = self.getFTPCatalog(self.urls['essences'])

		return essences


	def updateEssence(self, essence):
		'Получает файлы сущностей для анализа и обработки'

		# Импортируем
		from io import TextIOWrapper

		# Получаем список файлов
		catalog = "/{}/{}".format(self.urls['essences'], self.urls[essence])
		zip_names = self.getFTPCatalog(catalog)

		# Загружаем архивы
		for zip_name in zip_names:

			# Скачиваем архив
			zip_data = self.getZipFromFTP(zip_name, catalog)
			print("Скачал файл {}, тип объекта {}.".format(zip_name, type(zip_data)))

			# Получаем список файлов в архиве
			xml_names = zip_data.namelist()
			for xml_name in xml_names:

				# Извлекаем файл из архива
				xml_data = zip_data.open(xml_name)
				print("Извлек файл {} типа {} из архива {}.".format(xml_name, type(xml_data), zip_name))

				# Парсим файл
				if   'country'  == essence: self.parseCountry(xml_data)
				elif 'currency' == essence: self.parseCurrency(xml_data)
				elif 'okei'     == essence: self.parseOKEI(xml_data)
				elif 'kosgu'    == essence: self.parseKOSGU(xml_data)
				elif 'okopf'    == essence: self.parseOKOPF(xml_data)
				elif 'okpd'     == essence: self.parseOKPD(xml_data)
				elif 'oktmo'    == essence: self.parseOKTMO(xml_data)
				# TODO
				# TODO
				# TODO
				# TODO
				# TODO
				else: print('Ошибка: отсутствует парсер для сущности {}.'.format(essence))

				print("Файл {} обработан.".format(xml_name))

		return True


	def parseCountry(self, xml_data):
		'Парсит страны'

		# Импортируем
		from lxml import etree

		# Парсим
		tree = etree.parse(xml_data)

		# Получаем корневой элемент
		root = tree.getroot()

		# Получаем список
		for country_list in root:

			# Получаем элемент
			for country in country_list:

				# Инициируем пустой справочник элемента
				e = {}

				# Обрабатываем значения полей
				for value in country:
					if   value.tag.endswith('countryCode'):
						e['code'] = value.text
					elif value.tag.endswith('countryFullName'):
						e['full_name'] = value.text
					elif value.tag.endswith('actual'):
						if value.text == 'true':
							e['state'] = True
						else:
							e['state'] = False

				# Обновляем информацию в базе
				country = Country.objects.update(
					code         = e['code'],
					full_name    = e['full_name'],
					state        = e['state'])

				print("Обновлена страна: {}.".format(country.full_name))

		return True


	def parseCurrency(self, xml_data):
		'Парсит валюты'

		# Импортируем
		from lxml import etree

		# Парсим
		tree = etree.parse(xml_data)

		# Получаем корневой элемент
		root = tree.getroot()

		# Получаем список
		for currency_list in root:

			# Получаем элемент
			for currency in currency_list:

				# Инициируем пустой справочник элемента
				e = {}

				# Обрабатываем значения полей
				for value in currency:
					if   value.tag.endswith('code'):
						e['code'] = value.text
					elif value.tag.endswith('digitalCode'):
						e['digital_code'] = value.text
					elif value.tag.endswith('name'):
						e['name'] = value.text
					elif value.tag.endswith('actual'):
						if value.text == 'true':
							e['state'] = True
						else:
							e['state'] = False

				# Обновляем информацию в базе
				currency = Currency.objects.update(
					code         = e['code'],
					digital_code = e['digital_code'],
					name         = e['name'],
					state        = e['state'])

				print("Обновлена валюта: {}.".format(currency.code))

		return True


	def parseOKEI(self, xml_data):
		'Парсит единицы измерения'

		# Импортируем
		from lxml import etree

		# Парсим
		tree = etree.parse(xml_data)

		# Получаем корневой элемент
		root = tree.getroot()

		# Получаем список
		for okei_list in root:

			# Получаем элемент
			for okei in okei_list:

				# Инициируем пустой справочник элемента
				e = {}

				# Обрабатываем значения полей
				for value in okei:

					# code
					if value.tag.endswith('code'):
						e['code'] = value.text

					# full_name
					elif value.tag.endswith('fullName'):
						e['full_name'] = value.text

					# section
					elif value.tag.endswith('section'):

						for section_value in value:

							if section_value.tag.endswith('code'):
								e['section_code'] = section_value.text
							elif section_value.tag.endswith('name'):
								e['section_name'] = section_value.text

					# group
					elif value.tag.endswith('group'):

						for group_value in value:

							if group_value.tag.endswith('id'):
								e['group_code'] = group_value.text
							elif group_value.tag.endswith('name'):
								e['group_name'] = group_value.text

					# local_name
					elif value.tag.endswith('localName'):
						e['local_name'] = value.text

					# international_name
					elif value.tag.endswith('internationalName'):
						e['international_name'] = value.text

					# local_symbol
					elif value.tag.endswith('localSymbol'):
						e['local_symbol'] = value.text

					# international_symbol
					elif value.tag.endswith('internationalSymbol'):
						e['international_symbol'] = value.text

					# state
					elif value.tag.endswith('actual'):
						if value.text == 'true':
							e['state'] = True
						else:
							e['state'] = False

				# Обновляем информацию в базе
				okei_section = OKEISection.objects.update(
					code         = e['section_code'],
					name         = e['section_name'],
					state        = True)
				okei_group = OKEIGroup.objects.update(
					code         = e['group_code'],
					name         = e['group_name'],
					state        = True)
				okei = OKEI.objects.update(
					code                 = e['code'],
					full_name            = e['full_name'],
					section              = okei_section,
					group                = okei_group,
					local_name           = e['local_name'],
					international_name   = e['international_name'],
					local_symbol         = e['local_symbol'],
					international_symbol = e['international_symbol'],
					state                = e['state'])

				print("Обновлена единица измерения: {}.".format(okei.full_name))

		return True


	def parseKOSGU(self, xml_data):
		'Парсит классификатор операций сектора государственного управления.'

		# Импортируем
		from lxml import etree

		# Парсим
		tree = etree.parse(xml_data)

		# Получаем корневой элемент
		root = tree.getroot()

		# Получаем список
		for element_list in root:

			# Получаем элемент
			for element in element_list:

				# Инициируем пустой справочник элемента
				e = {}

				# Обрабатываем значения полей
				for value in element:

					# code
					if value.tag.endswith('code'):
						e['code'] = value.text

					# parent_code
					elif value.tag.endswith('parentCode'):
						if not value.text or value.text == '000':
							e['parent_code'] = None
						else:
							e['parent_code'] = value.text
	
					# name
					elif value.tag.endswith('name'):
						e['name'] = value.text

					# state
					elif value.tag.endswith('actual'):
						if value.text == 'true':
							e['state'] = True
						else:
							e['state'] = False

				# Обновляем информацию в базе
				try:
					e['parent_code'] = e['parent_code']
				except KeyError:
					e['parent_code'] = None

				kosgu = KOSGU.objects.update(
					code        = e['code'],
					parent_code = e['parent_code'],
					name        = e['name'],
					state       = e['state'])

				print("Обновлён элемент КОСГУ: {} {}.".format(kosgu.code, kosgu.name))

		return True


	def parseOKOPF(self, xml_data):
		'Парсит ОКОПФ.'

		# Импортируем
		from lxml import etree

		# Парсим
		tree = etree.parse(xml_data)

		# Получаем корневой элемент
		root = tree.getroot()

		# Получаем список
		for element_list in root:

			# Получаем элемент
			for element in element_list:

				# Инициируем пустой справочник элемента
				e = {}

				# Обрабатываем значения полей
				for value in element:

					# code
					if value.tag.endswith('code'):
						e['code'] = value.text

					# parent_code
					elif value.tag.endswith('parentCode'):
						if not value.text:
							e['parent_code'] = None
						else:
							e['parent_code'] = value.text
	
					# full_name
					elif value.tag.endswith('fullName'):
						e['full_name'] = value.text

					# singular_name
					elif value.tag.endswith('singularName'):
						e['singular_name'] = value.text

					# state
					elif value.tag.endswith('actual'):
						if value.text == 'true':
							e['state'] = True
						else:
							e['state'] = False

				# Обновляем информацию в базе
				try:
					e['parent_code'] = e['parent_code']
				except KeyError:
					e['parent_code'] = None

				print(e)

				okopf = OKOPF.objects.update(
					code          = e['code'],
					parent_code   = e['parent_code'],
					full_name     = e['full_name'],
					singular_name = e['singular_name'],
					state         = e['state'])

				print("Обновлён элемент ОКОПФ: {} {}.".format(okopf.code, okopf.full_name))

		return True


	def parseOKPD(self, xml_data):
		'Парсит ОКПД.'

		# Импортируем
		from lxml import etree

		# Парсим
		tree = etree.parse(xml_data)

		# Получаем корневой элемент
		root = tree.getroot()

		# Получаем список
		for element_list in root:

			# Получаем элемент
			for element in element_list:

				# Инициируем пустой справочник элемента
				e = {}

				# Обрабатываем значения полей
				for value in element:

					# code
					if value.tag.endswith('id'):
						e['code'] = value.text

					# parent_code
					elif value.tag.endswith('parentId'):
						if not value.text:
							e['parent_code'] = None
						else:
							e['parent_code'] = value.text

					# alias
					elif value.tag.endswith('code'):
						e['alias'] = value.text	

					# name
					elif value.tag.endswith('name'):
						e['name'] = value.text

					# state
					elif value.tag.endswith('actual'):
						if value.text == 'true':
							e['state'] = True
						else:
							e['state'] = False

				# Обновляем информацию в базе
				try:
					e['parent_code'] = e['parent_code']
				except KeyError:
					e['parent_code'] = None

				print(e)

				okpd = OKPD.objects.update(
					code        = e['code'],
					parent_code = e['parent_code'],
					alias       = e['alias'],
					name        = e['name'],
					state       = e['state'])

				print("Обновлён элемент ОКДП: {} {}.".format(okpd.alias, okpd.name))

		return True


	def parseOKTMO(self, xml_data):
		'Парсит ОКТМО.'

		# Импортируем
		from lxml import etree

		# Парсим
		tree = etree.parse(xml_data)

		# Получаем корневой элемент
		root = tree.getroot()

		# Получаем список
		for element_list in root:

			# Получаем элемент
			for element in element_list:

				# Инициируем пустой справочник элемента
				e = {}

				# Обрабатываем значения полей
				for value in element:

					# code
					if value.tag.endswith('code'):
						e['code'] = value.text

					# parent_code
					elif value.tag.endswith('parentCode'):
						if not value.text:
							e['parent_code'] = None
						else:
							e['parent_code'] = value.text

					# full_name
					elif value.tag.endswith('fullName'):
						e['full_name'] = value.text

					# state
					elif value.tag.endswith('actual'):
						if value.text == 'true':
							e['state'] = True
						else:
							e['state'] = False

				# Обновляем информацию в базе
				try:
					e['parent_code'] = e['parent_code']
				except KeyError:
					e['parent_code'] = None

				print(e)

				oktmo = OKTMO.objects.update(
					code        = e['code'],
					parent_code = e['parent_code'],
					full_name   = e['full_name'],
					state       = e['state'])

				print("Обновлён элемент ОКТМО: {}.".format(oktmo.full_name))

		return True



	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser
	# TODO Parser


	def updateRegions(self):
		'Обновляет список регионов'

		# Черный лист
		black_list = ['_logs']

		# Получаем список регионов с FTP-сервера
		regions = self.getFTPCatalog(self.urls['regions'])
		print('Получен список регионов.')

		for region in regions:

			if not region in black_list:
				region = Region.objects.take(
					alias = region,
					name = region,
					full_name = region)

		return True


