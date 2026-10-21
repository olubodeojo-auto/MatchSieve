from matchsieve.provider_manager import ProviderManager
from matchsieve.repository import Repository
print(ProviderManager(Repository()).catalog())
