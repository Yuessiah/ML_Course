import numpy as np
from random import randint
import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    comm.ml_ready()
    comm.send_instruction(comm.get_scene_info().frame, PlatformAction.SERVE_TO_LEFT)

    predictx = 95
    ballx, bally = 95, 400
    while True:
        scene_info = comm.get_scene_info()

        if scene_info.status == GameStatus.GAME_OVER:
            break

        ballspeedx = scene_info.ball[0] + 2.5 - ballx
        ballspeedy = scene_info.ball[1] + 2.5 - bally
        ballx = scene_info.ball[0] + 2.5
        bally = scene_info.ball[1] + 2.5
        platformx = scene_info.platform[0] + 20

        dir = 1
        for i in range(30):
            if ballx+i*ballspeedx < 0 or bally+i*ballspeedy < 0 or \
            ballx+i*ballspeedx > 200 or bally+i*ballspeedy > 400:
                break
            for j in range(-30, 30):
                if (int(ballx+i*ballspeedx+j), int(bally+i*ballspeedy)) in scene_info.bricks:
                    dir = -1
                    break

        if (ballspeedy > 0) and (bally > 257):
            predictx = ballx + dir*(ballspeedx * (400 - bally)/ballspeedy) + randint(-3, 3)
        elif (ballspeedy < 0) and (bally > 257):
            predictx = ballx + dir*(ballspeedx * (400 - bally)/ballspeedy) + randint(-7, 7)
        elif ballspeedy == 0:
            predictx = 95 + 2.2*randint(-11, 11)
        else:
            predictx = 95


        if platformx == predictx:
            comm.send_instruction(scene_info.frame, PlatformAction.NONE)
        elif platformx > predictx:
            comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
        elif platformx < predictx:
            comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
