import typing

from .. import BaseProvider


class Provider(BaseProvider):
    """
    Base Provider for Persona.
    
    A Persona generates a logically consistent virtual portrait based on geographic and logical constraints,
    going beyond simple fields generation to orchestrate multiple facts (SSN, Phone, etc.) tightly.
    """
    
    def persona(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """
        Generate a logically consistent persona.
        Must be implemented by localized providers.
        """
        raise NotImplementedError("Persona generation is only available in localized providers.")

