#% extends "resource_parent.py" 
#{% block topblockimport %}from top_block import top_block
#{% endblock %}


#{% block addpropertychangelisteners %}
self.addPropertyChangeListener('gr::multiplier', self.gr_multiplier_changed)
		self.gr_multiplier_changed('gr::multiplier', 0, self.gr_multiplier)
#{% endblock %}

#{% block propertychanged %}
def gr_multiplier_changed(self, id, old_value, new_value):

		self.tb.set_multiplier(new_value)
		self.gr_multiplier = self.tb.get_multiplier()
#{% endblock %}
#{% block start %}
copy_mult_pass_base.start(self)
#{% endblock %}
#{% block stop %}
copy_mult_pass_base.stop(self)
#{% endblock %}
#{% block getport %}
if name == "dataShort_in":
			return self.tb.redhawk_integration_redhawk_source_0.getPort("dataShort_in")
		if name == "dataShort_out":
			return self.tb.redhawk_integration_redhawk_sink_0.getPort("dataShort_out")
#{% endblock %}