from django.conf.urls import patterns, url

from tenders import views

urlpatterns = patterns('',


	# Updater
	# ex: /tenders/updaters/
	url(r'^updaters/$', views.updaters, name='updaters'),
	# AJAX
	url(r'^ajax/get-updater/$', views.ajaxGetUpdater, name='ajaxGetUpdater'),
	url(r'^ajax/save-updater/$', views.ajaxSaveUpdater, name='ajaxSaveUpdater'),
	url(r'^ajax/switch-updater-state/$', views.ajaxSwitchUpdaterState, name='ajaxSwitchUpdaterState'),


	# Region
	# ex: /tenders/regions/
	url(r'^regions/$', views.regions, name='regions'),
	# AJAX
	url(r'^ajax/get-region/$', views.ajaxGetRegion, name='ajaxGetRegion'),
	url(r'^ajax/save-region/$', views.ajaxSaveRegion, name='ajaxSaveRegion'),
	url(r'^ajax/switch-region-state/$', views.ajaxSwitchRegionState, name='ajaxSwitchRegionState'),


	# Organisation
	# AJAX
	url(r'^ajax/get-organisation/$', views.ajaxGetOrganisation, name='ajaxGetOrganisation'),


	# Plan Graph
	# ex: /tenders/plan-graphs/
	url(r'^plan-graphs/$', views.planGraphs, name='planGraphs'),


	# Plan Graph Position
	# ex: /tenders/plan-graph-positions/
	url(r'^plan-graph-positions(/query/(?P<query>[0-9]+)){0,1}(/page/(?P<page>[0-9]+)){0,1}/$', views.planGraphPositions, name='planGraphPositions'),
	# AJAX
	url(r'^ajax/get-plan-graph-position/$', views.ajaxGetPlanGraphPosition, name='ajaxGetPlanGraphPosition'),

	# Query Filter
	# ex: /tenders/query-filter/
	url(r'^query-filters/$', views.queryFilters, name='queryFilters'),
	# AJAX
	url(r'^ajax/get-queryfilter/$',           views.ajaxGetQueryFilter,          name='ajaxGetQueryFilter'),
	url(r'^ajax/save-queryfilter/$',          views.ajaxSaveQueryFilter,         name='ajaxSaveQueryFilter'),
	url(r'^ajax/switch-queryfilter-state/$',  views.ajaxSwitchQueryFilterState,  name='ajaxSwitchQueryFilterState'),
	url(r'^ajax/switch-queryfilter-public/$', views.ajaxSwitchQueryFilterPublic, name='ajaxSwitchQueryFilterPublic'),

	# Eccences
	# ex: /tenders/eccences/
	url(r'^essences/$', views.essences, name='essences'),
	url(r'^essence/okpd/$', views.OKPDs, name='OKPDs'),

)
