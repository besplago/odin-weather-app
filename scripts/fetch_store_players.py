from balldontlie import BalldontlieAPI
from balldontlie.base import PaginatedListResponse
from balldontlie.nba.models import NBAPlayer

api: BalldontlieAPI = BalldontlieAPI(api_key="ab7d3912-b6a7-42f1-acec-11659c260395")
players: PaginatedListResponse[NBAPlayer] = api.nba.players.list(per_page=100, cursor=100)
print(len(players.data))
for player in players.data:
    print(player.last_name)
