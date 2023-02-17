from quest.core.manager import Manager

from IdleKnights import IdleTeam
from IdleKnights.charaters import make_character
from IdleKnights.charaters.castleseeker import SpeedyKnight
from IdleKnights.charaters.castlekiller import DeadlyKnight
from IdleKnights.logic.searching import king_defender

from IdleKnights.tournament.king import team

GAME_MODE = "king"
SPEEDUP = 1.25
ANGRY = {
    'health_ratio':   0.15,
    'distance_ratio': 0.1,
    'fight_ratio':    0.2,
    'gem_ratio':      1/2,
}

team2 = IdleTeam('AI1',
                Caspar1=make_character(DeadlyKnight, index=0, mode=GAME_MODE, initial_mode=king_defender,
                                      inject_kwargs=ANGRY),
                Melchior1=make_character(DeadlyKnight, index=0, mode=GAME_MODE, initial_mode=king_defender,
                                        inject_kwargs=ANGRY),
                Balthazar1=make_character(DeadlyKnight, index=1, mode=GAME_MODE, initial_mode=king_defender,
                                         inject_kwargs=ANGRY))

team3 = IdleTeam('AI2',
                       Ruohtta2=make_character(SpeedyKnight, index=0, mode=GAME_MODE),
                       Parnashavari2=make_character(DeadlyKnight, index=1, mode=GAME_MODE),
                       Matarajin2=make_character(DeadlyKnight, index=0, mode=GAME_MODE))

manager = Manager(team, team2, team3)


while ((match := manager.next_match()) is not None):
    input(f'Next match is: {match.to_string()}')
    match.best_of = 1
    match.play(speedup=1, show_messages=False, safe=True)
    manager.show_scores()

manager.show_scores()
input('End of tournament!')
