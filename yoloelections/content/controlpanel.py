"""

    Define add-on settings.

"""

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from zope import schema
from zope.interface import Interface


class IElectionsSettings(Interface):
    """ Define settings data structure """

    # form.widget(upcoming_elections='z3c.form.browser.textlines.TextLinesFieldWidget')
    upcoming_elections = schema.List(
        title=u'Upcoming Elections',
        description=u"""
            Set the list of upcoming elections for the "next_election" field.
            Format is code|title, one per line; e.g., G2020|November, 2020""",
        required=False,
        default=['None|Unscheduled'],
        value_type=schema.ASCIILine(title=u'Election'),
    )


class SettingsEditForm(RegistryEditForm):
    """
    Define form
    """
    schema = IElectionsSettings
    label = u"Elections settings"


class SettingsControlPanel(ControlPanelFormWrapper):
    """
    View
    """
    form = SettingsEditForm
