from anyblok import Declarations

register = Declarations.register
Model = Declarations.Model


@register(Model)
class BandManagement:
    """Namespace for Band Management related models and transversal methods.

    Since this Model does not have any persistent data, making instances of
    it is mostly irrelevant, and therefore, the transversal methods are
    classmethods.
    """
