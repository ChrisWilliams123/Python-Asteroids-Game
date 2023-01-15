import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
startlives=3
lives = startlives
time = 0.5
started = False


inc_angvel=0.04
init_vel=[0,0]
init_angle=-math.pi/2.0
unit_acc=0.1
unit_friction=0.02
missilespeed=7
rock_speed_init=2.5
rock_speed=rock_speed_init
rockmax=12
fontsize=32

SCREEN_SIZE=[WIDTH,HEIGHT]

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects
    

debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 70)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")


# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


def process_sprite_group(spritegroup,canvas):   
    spriteset=set(spritegroup)
    for sprite in spriteset:
         sprite.draw(canvas)
         if sprite.update():
            spritegroup.discard(sprite)

def process_ship(shipobject,canvas):
    shipobject.draw(canvas)
    shipobject.update()

def group_collide(group,other_object):
    groupset=set(group)
    returnvalue=False
    for group_object in groupset:
        if group_object.collide(other_object):
            group.discard(group_object)
            returnvalue=True
            explosion_group.add(Sprite(group_object.get_position(),[0,0],0,0,explosion_image,explosion_info))
            if explosion_sound:
                explosion_sound.rewind()
                explosion_sound.play()           
    return returnvalue

def group_group_collide(group1,group2):
    group1set=set(group1)
    removecount=0
    for group1_object in group1set:
        if group_collide(group2,group1_object):
            removecount+=1
            group1.discard(group1_object)
    return removecount

def initialize():
    global started,score,lives,rock_group,missile_group,my_ship,explosion_group
    
    started=False
    score=0
    lives=startlives
    rock_group=set([])
    missile_group=set([])
    rock_speed=rock_speed_init
    my_ship.reset()
    if soundtrack:
       soundtrack.pause()
 

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image 
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.forward_vector=[0,-1]
   
    def get_position(self):
        return self.pos
    def get_radius(self):
        return self.radius     
    
    def draw(self,canvas):
        canvas.draw_image(self.image,self.image_center, self.image_size, self.pos, self.image_size, self.angle)
    
    def reset(self):
        self.pos =[WIDTH / 2, HEIGHT / 2]
        self.vel = [0,0]
        self.angle=init_angle
        self.thrust = False
        self.angle_vel = 0
        self.forward_vector=[0,-1]
        
    def update(self):
        
        self.forward_vector=angle_to_vector(self.angle)
        for axis in range(0,2):
            if self.thrust:
                self.vel[axis]+=unit_acc*self.forward_vector[axis]
            self.vel[axis]*=(1-unit_friction)
            self.pos[axis]+=self.vel[axis]
            self.pos[axis]=self.pos[axis]%SCREEN_SIZE[axis]
            
        self.angle+=self.angle_vel
        
    def rot(self,mult):
        self.angle_vel+=mult*inc_angvel

        
    def rot_zero(self,mult):
        self.angle_vel=0

    def thrustswitch(self,val):
        if isinstance(val,bool):
            self.thrust = val
        
        if self.thrust and started:
            self.image_center=[ship_info.get_center()[0]+self.image_size[0],ship_info.get_center()[1]]
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            self.image_center = ship_info.get_center()
            ship_thrust_sound.rewind()
    
    def shoot(self,mult):
        global missile_group
        
        spawn_pos=[0,0]
        spawn_vel=[0,0]
        for axis in range(0,2):
            spawn_pos[axis]=self.pos[axis]+self.radius*self.forward_vector[axis]
            spawn_vel[axis]=self.vel[axis]+mult*self.forward_vector[axis]
            
        if started:
            missile_group.add(Sprite(spawn_pos, spawn_vel, 0, 0, missile_image, missile_info, missile_sound))

    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None,size_multiple=1):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.final_image_size=[size_multiple*info.get_size()[0],size_multiple*info.get_size()[1]]
        self.radius = size_multiple*info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
            
    def get_position(self):
        return self.pos
    def get_radius(self):
        return self.radius
   
    def draw(self, canvas):      
        if self.animated:
            center=[self.image_center[0]+self.age*self.image_size[0],self.image_center[1]]
            canvas.draw_image(self.image,center, self.image_size, self.pos, self.final_image_size, self.angle)
        else:
            canvas.draw_image(self.image,self.image_center, self.image_size, self.pos, self.final_image_size, self.angle)
    
    def update(self):
        for axis in range(0,2):
            self.pos[axis]+=self.vel[axis]
            self.pos[axis]=self.pos[axis]%SCREEN_SIZE[axis]
            
        self.angle+=self.angle_vel
        self.age+=1
        if self.age>=self.lifespan:
            return True
        else:
            return False
        
    def collide(self,other_sprite):
        if dist(self.pos,other_sprite.get_position())<=self.radius+other_sprite.get_radius():
            return True
        else:
            return False 
               
     
def draw(canvas):
    global time,lives,score,rock_group,missile_group,started,rock_speed,explosion_group
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

       # draw UI
    canvas.draw_text('Score: '+str(score), (WIDTH-150, 40), fontsize, 'Red')
    canvas.draw_text('Lives: '+str(lives), (40, 40), fontsize, 'Red')
    
    
    score+=group_group_collide(rock_group,missile_group)
    rock_speed=rock_speed_init + 1.0*(score//3)
    
    if group_collide(rock_group,my_ship):
        lives-=1 
    
    if lives<1:
        explosion_group.add(Sprite(my_ship.get_position(),[0,0],0,0,explosion_image,explosion_info))
        if explosion_sound:
            explosion_sound.rewind()
            explosion_sound.play()
        initialize()
       
    
    # draw splash screen if not started
    if not started:
        process_sprite_group(explosion_group,canvas)
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
    else:
        process_sprite_group(rock_group,canvas)
        process_sprite_group(missile_group,canvas)
        process_sprite_group(explosion_group,canvas)
        process_ship(my_ship,canvas)
        
            
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group  
    if len(rock_group)<rockmax and started:      
        side=random.randrange(0,2)
        spawn_pos=[side*random.randrange(0,SCREEN_SIZE[0]),((side-1)**2)*random.randrange(0,SCREEN_SIZE[1])]
        spawn_vel=[rock_speed*(2*random.random()-1),rock_speed*(2*random.random()-1)]
        spawn_rot=3*inc_angvel*(2*random.random()-1)
        spawn_size=1.4*random.random()+0.3
        rock_group.add(Sprite(spawn_pos, spawn_vel, 2*math.pi*random.random(),spawn_rot, asteroid_image, asteroid_info, None,spawn_size))

 
def click(pos):
    global started
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        if soundtrack:
            soundtrack.rewind()
            soundtrack.play()
     
def keydown(key):
    for i in inputs_down:
        if key == simplegui.KEY_MAP[i]:
            inputs_down[i][0](inputs_down[i][1])

            
def keyup(key):
     for i in inputs_up:
        if key == simplegui.KEY_MAP[i]:
            inputs_up[i][0](inputs_up[i][1])

    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

my_ship = Ship([WIDTH / 2, HEIGHT / 2], init_vel, init_angle, ship_image, ship_info)
explosion_group=set([])
initialize()


inputs_down = {"up": [my_ship.thrustswitch, True],
          "down": [my_ship.rot, 0],
          "left": [my_ship.rot, -1],
          "right": [my_ship.rot, +1],
          "space": [my_ship.shoot, missilespeed]}
inputs_up = {"up": [my_ship.thrustswitch,False],
          "down": [my_ship.rot_zero,0],
          "left": [my_ship.rot_zero,0],
          "right": [my_ship.rot_zero,0]}

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things going
timer.start()
frame.start()



