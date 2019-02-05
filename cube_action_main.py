import cozmo
import asyncio

from colors import Colors
from cozmo.util import distance_mm
from cozmo.objects import LightCube


# region CubeAction Class
class CubeAction:
    def __init__(self, robot: cozmo.robot.Robot):
        self.robot = robot
        self.cubes = []

    async def move_to_cube(self, cube):
        await self.robot.go_to_object(cube, distance_mm(100.0)).wait_for_completed()
        await self.robot_say(f'Moved to cube {cube.cube_id}')

    async def on_cube_tapped(self, evt, obj: LightCube, **kwargs):
        obj.set_lights(Colors.RED)
        if obj.cube_id == 1:
            await self.robot_say('I will move to the cube')
            await self.move_to_cube(obj)
        elif obj.cube_id == 2:
            await self.robot_say('You tapped the picture cube, smile!')

            # Find a face to take a photo of
            find_faces = self.robot.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)
            found_face = await self.robot.world.wait_for_observed_face(timeout=120)
            find_faces.stop()

            await self.robot.turn_towards_face(found_face).wait_for_completed()

            # Grab the latest frame and save the raw image as a greyscale png file
            img_latest = self.robot.world.latest_image.raw_image.convert('L')
            img_latest.save('cozmoPhoto.png', 'png')

            await self.robot_say('You look great! I saved the image for you.')
        elif obj.cube_id == 3:
            await self.robot.play_anim(name='anim_codelab_rattle_snake_01').wait_for_completed()
        obj.set_lights(Colors.BLUE)

    async def robot_say(self, text):
        await self.robot.say_text(text, duration_scalar=0.6).wait_for_completed()

    async def run(self):
        # Turn backpack lights to RED
        self.robot.set_all_backpack_lights(Colors.RED)

        # Settings for signals from Cozmo's camera
        self.robot.camera.image_stream_enabled = True

        # Connect to the cubes
        await self.robot.world.connect_to_cubes()

        # Begin looking around for objects
        await self.robot_say('Scanning for cubes')
        look_around = self.robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)

        # Find the cubes and store their information
        self.cubes = await self.robot.world.wait_until_observe_num_objects(num=3, object_type=LightCube, timeout=120)

        look_around.stop()

        await self.robot_say('I found the cubes')
        print(f'Found cubes: {self.cubes}')

        self.robot.set_all_backpack_lights(Colors.GREEN)

        for cube in self.cubes:
            # Set the lights on all the found cubes
            cube.set_lights(Colors.BLUE)

            # Add cube tap event handler with callback
            cube.add_event_handler(cozmo.objects.EvtObjectTapped, self.on_cube_tapped)

        await self.robot_say('Tap each cube to perform an action')


# endregion


async def cozmo_program(robot: cozmo.robot.Robot):
    cube_action = CubeAction(robot)
    await cube_action.run()

    # Wait to receive keyboard interrupt command to exit (CTRL-C)
    while True:
        await asyncio.sleep(0.5)


cozmo.run_program(cozmo_program, use_viewer=True, force_viewer_on_top=True)
