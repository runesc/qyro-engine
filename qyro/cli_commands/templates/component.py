COMPONENT_TEMPLATE = f"""
from qyro_engine.core.base import Component, init_lifecycle
from qyro_engine.store import Pydux
from $Binding.QtWidgets import $Widget

@init_lifecycle
class $Name($Widget, Component, Pydux):

	def component_will_mount(self):
		self.subscribe_to_store(self)

	def render_(self):
		# Render the UI here
		pass
"""