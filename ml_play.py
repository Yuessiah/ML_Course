"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
from random import randint

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    def move_to(player, pred) : #move platform to predicted position to catch ball
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-10) and scene_info["platform_1P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10) and scene_info["platform_2P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left

    def ml_loop_for_1P():
        ballspeedx = scene_info["ball_speed"][0]
        ballspeedy = scene_info["ball_speed"][1]
        ballx = scene_info["ball"][0] + 2.5
        bally = scene_info["ball"][1] + 2.5
        platformx = scene_info["platform_1P"][0] + 20
        blockerx = scene_info["blocker"][0]
        blockery = scene_info["blocker"][1]
        dir = 1

        for i in range(30):
            nxtx = ballx + i*ballspeedx
            nxty = bally + i*ballspeedy
            if (0 >= nxtx or nxtx >= 200):
                dir = -1
                break

        predictx = 100
        if ballspeedy > 0:
            if bally <= 270:
                predictx = ballx + dir*(ballspeedx * (420 - bally)/ballspeedy) # + randint(-3, 3)
            elif bally > 200:
                predictx = ballx + (ballspeedx * (420 - bally)/ballspeedy)
                if 70 <= predictx and predictx <= 130:
                    alpha = 2*ballspeedx//abs(ballspeedx)
                    predictx = predictx + randint(-3+alpha, 3+alpha)
                # predictx = 400 * ballx // bally
                print('pred = ', predictx, 'x = ', ballx, 'plat = ', platformx, 'y = ', bally)
        else:
            if 70 <= ballx and ballx <= 130:
                predictx = ballx
            else:
                predictx = 100

        if predictx == platformx: return 0
        if platformx < predictx: return 1
        if platformx > predictx: return 2


    def ml_loop_for_2P():  # as same as 1P
        if scene_info["ball_speed"][1] > 0 :
            return move_to(player = '2P',pred = 100)
        else :
            x = ( scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) // scene_info["ball_speed"][1]
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)
            bound = pred // 200
            if (bound > 0):
                if (bound%2 == 0):
                    pred = pred - bound*200
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) :
                if bound%2 ==1:
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            return move_to(player = '2P',pred = pred)

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # print('y = ', scene_info["ball"][1] + 2.5)

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
        else:
            if side == "1P":
                command = ml_loop_for_1P()
            else:
                command = ml_loop_for_2P()

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
