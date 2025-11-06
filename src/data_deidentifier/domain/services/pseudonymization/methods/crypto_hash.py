import hashlib
from typing import Any, override

from logger import LoggerContract

from src.data_deidentifier.domain.contracts.pseudonymizer.method import (
    PseudonymizationMethodContract,
)
from src.data_deidentifier.domain.types.entity import Entity


class CryptoHashPseudonymizationMethod(PseudonymizationMethodContract):
    """Cryptographic hash pseudonymization method using BLAKE2b."""

    PARAM_SALT = "salt"

    def __init__(self, params: dict[str, Any], logger: LoggerContract) -> None:
        """Initialize the cryptographic hash method.

        Args:
            params: Method parameters (salt, etc.)
            logger: Logger for logging events

        Raises:
            ValueError: If salt is provided but not a string
        """
        super().__init__(params=params, logger=logger)

        # Optional salt for security
        self._salt = self.params.get(self.PARAM_SALT, "")
        if self.PARAM_SALT in self.params and not isinstance(self._salt, str):
            raise ValueError("Salt must be a string")

        # Cache by entity type and text
        self._mapping: dict[str, dict[str, str]] = {}

    @override
    def generate_pseudonym(self, entity: Entity) -> str:
        """Generate a pseudonym using BLAKE2b hash.

        Args:
            entity: The original entity

        Returns:
            A pseudonym based on the hash of the entity
        """
        cache_key = entity.text
        entity_type = entity.type

        # Mapping by entity type
        if entity_type not in self._mapping:
            self._mapping[entity_type] = {}

        # Check if we already have a pseudonym for this entity
        entity_mapping = self._mapping.get(entity_type)
        if cache_key in entity_mapping:
            return entity_mapping.get(cache_key)

        # Create hash with salt and entity type for domain separation
        hash_input = f"{self._salt}{entity_type}:{entity.text}".encode()

        # Generate BLAKE2b hash (digest_size=8 gives us 64 bits)
        # BLAKE2b is not vulnerable to length extension attacks
        hash_bytes = hashlib.blake2b(hash_input, digest_size=8).digest()
        hash_hex = hash_bytes.hex().upper()

        # Format as pseudonym
        pseudonym = f"<{entity_type}_{hash_hex}>"

        # Store in cache
        self._mapping[entity_type][cache_key] = pseudonym
        return pseudonym
