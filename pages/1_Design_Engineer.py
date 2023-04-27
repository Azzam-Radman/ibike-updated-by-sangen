import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
import cv2 as cv


st.set_page_config(page_title='Design Engineer')
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("Welcome to the Design Engineer Page!")

st.markdown(
    """
    Your role revolves around selecting the design parameters of the bike so as to maximize its stability. You
    will be provided with the set of the parameters with brief description.
    """)

st.markdown('---')

st.image('design_eng_1.png')
st.markdown('---')
st.image('design_eng_2.png')
st.markdown('---')
#st.image('design_eng_3.png')
#st.markdown('---')

# Input parameters

w = st.slider('Insert Wheel base (m)', min_value=0.8, max_value=1.2, value=0.8, step=0.01)

c=0.08; # Trail (m)
lamda=np.pi/10; # Steer axis tilt (rad)
g=9.81; # Gravitational acceleration (N/kg or m/s)
#v=zeros(100,1);# Forward velocity of bicycle (m/s)
# Rear wheel, R

rR = st.slider('Rear Wheel Radius (m)', min_value=0.3, max_value=0.4, value=0.3, step=0.01)

mR=2; # Mass (kg)
IRxx=0.0603; # Mass moments of inertia (kg m^2) 
IRyy=0.0603; # Mass moments of inertia (kg m^2)
# Read body and frame assembly, B
xB=0.3; # Position of center of mass (m)
zB=-0.9; # Position of center of mass (m)

mB = st.slider('Mass (kg)', min_value=50, max_value=100, value=50)

IBxx=9.2; # Mass moment of inertia (kg m^2)
IByy=11; # Mass moment of inertia (kg m^2)
IBzz=2.8; # Mass moment of inertia (kg m^2)
IBxz=0; # Mass moment of inertia (kg m^2)
# Front handlebar and fork assembly, H
xH=0.91; # Position of center of mass (m)
zH=-0.68; # Position of center of mass (m)
mH=4; # Mass (kg)
IHxx=0.05892; # Mass moment of inertia (kg m^2)
IHyy=0.12; # Mass moment of inertia (kg m^2)
IHzz=0.00708; # Mass moment of inertia (kg m^2)
IHxz=0; # Mass moment of inertia (kg m^2)
# Front wheel, F

rF = st.slider('Fron Wheel Radius (m)', min_value=0.3, max_value=0.4, value=0.3, step=0.01)

mF=3; # Mass (kg)
IFxx=0.1405; # Mass moments of inertia (kg m^2) 
IFyy=0.1405; # Mass moments of inertia (kg m^2)

# Calculation
# Total mass and center of mass location with respect to rear contact point p 

mT=mR+mB+mH+mF; # B 1
xT=(xB*mB+xH*mH+w*mF)/mT; # B 2
zT=(-rR*mR+zB*mB+zH*mH-rF*mF)/mT; # B 3 
# Relevant mass moments and products of inertia with respect to rear contact point P
ITxx=IRxx+IBxx+IHxx+IFxx+mR*rR**2+mB*zB**2+mH*zH**2+mF*rF**2; # B 4
ITxz=IBxz+IHxz-mB*xB*zB-mH*xH*zH+mF*w*rF; # B 5
IRzz=IRxx; IFzz=IFxx; # B 6
ITzz=IRzz+IBzz+IHzz+IFzz+mB*xB**2+mH*xH**2+mF*w**2; # B 7
# Total mass, center of location, and mass moment of inertia with respect to rear contact point P
mA=mH+mF; # B 8
xA=(xH*mH+w*mF)/mA; zA=(zH*mH-rF*mF)/mA; # B 9
IAxx=IHxx+IFxx+mH*(zH-zA)**2+mF*(rF+zA)**2; # B 10
IAxz=IHxz-mH*(xH-xA)*(zH-zA)+mF*(w-xA)*(rF+zA); # B 11
IAzz=IHzz+IFzz+mH*(xH-xA)**2+mF*(w-xA)**2; # B 12
# The center of mass of the front assembly form the center of mass of front wheel
uA=(xA-w-c)*np.cos(lamda)-zA*np.sin(lamda); # B 13
# Three special inertia quantities
IAll=mA*uA**2+IAxx*(np.sin(lamda))**2+2*IAxz*np.sin(lamda)*np.cos(lamda)+IAzz*(np.cos(lamda))**2; # A 14
IAlx=-mA*uA*zA+IAxx*np.sin(lamda)+IAxz*np.cos(lamda); # B 15
IAlz=mA*uA*xA+IAxz*np.sin(lamda)+IAzz*np.cos(lamda); # B 16
# The ratio of mechanical trail
nu=(c/w)*np.cos(lamda); # B 17
# Gyroscopic coefficients
SR=IRyy/rR; SF=IFyy/rF; ST=SR+SF; # B 18
SA=mA*uA+nu*mT*xT; # B 19
# Mass Matrix, M
M=np.zeros((2, 2));
M[0,0]=ITxx; M[0,1]=IAlx+nu*ITxz; M[1,0]=M[0,1]; 
M[1,1]=IAll+2*nu*IAlz+nu**2*ITzz; # A 20

# Gravity-dependent stiffness matrix, Ko
Ko=np.zeros((2, 2));
Ko[0,0]=mT*zT; Ko[0,1]=-SA; Ko[1,0]=Ko[0,1]; Ko[1,1]=-SA*np.sin(lamda); # B 22

# Velocity-dependent stiffness matrix, K2
K2=np.zeros((2, 2));
K2[0,0]=0; K2[0,1]=((ST-mT*zT)/w)*np.cos(lamda); K2[1,0]=0; 
K2[1,1]=((SA+SF*np.sin(lamda))/w)*np.cos(lamda); # A 24

# Damping-like matrix, C
C=np.zeros((2, 2));
C[0,0]=0; C[0,1]=nu*ST+SF*np.cos(lamda)+(ITxz/w)*np.cos(lamda)-nu*mT*zT; 
C[1,0]=-(nu*ST+SF*np.cos(lamda)); 
C[1,1]=(IAlz/w)*np.cos(lamda)+nu*(SA+(ITzz/w)*np.cos(lamda)); # B 26

########################################################
# Finding eigenvalues
v = sp.symbols('v', real=True)
sigma = sp.symbols('sigma', real=True)
EOM=M*sigma**2+v*C*sigma+g*Ko+v**2*K2;
EOM = sp.Matrix(EOM)
d = EOM.det()
s=sp.solveset(d, sigma)
vel=np.zeros((100,1));
sol=np.zeros((100,4), dtype=complex);
for i in range (1, 101):
    vel[i-1,0] = i/10;
    aa = s.subs(v, i/10) 
    sol[i-1,:] = np.fromiter(aa, dtype=complex)

real_sol=np.real(sol)
real_sol_index=np.where(np.sum(real_sol < 0, axis=1) == 4)[0]
########################################################
with st.spinner('Wait for it...'):
    plt.figure(figsize=(12, 8))
    plt.plot(vel, real_sol, linewidth=2)
    plt.plot(vel[real_sol_index[0]]*np.ones((len(vel),1)), np.linspace(-30, 11,len(vel)), linestyle='--', linewidth=3)
    plt.plot(vel[real_sol_index[-1]]*np.ones((len(vel),1)), np.linspace(-30, 11,len(vel)), linestyle='--', linewidth=3)
    plt.title('Solution roots vs. velocity diagram of the standard model')
    plt.xlabel('Velocity (m/s)')
    plt.ylabel('Real part of the Solution roots')
    plt.grid(linestyle='-.')
st.pyplot()

########################################################
plt.figure(figsize=(12, 8))
h = int(1024*(8/12))
w = 1024
img = 255 * np.ones((h, w, 3), np.uint8)

radius_1 = 100
center_coordinates_1 = (200, h - radius_1-100)

length = 300
radius_2 = 100
center_coordinates_2 = (200+length, h - radius_2-100)

color = (0, 0, 0)
thickness = 2


pt3 = center_coordinates_1[0] - radius_1
pt4 = center_coordinates_1[1]
img = cv.line(img, center_coordinates_1, (pt3, pt4), (255, 0, 0), 2)

font                   = cv.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = center_coordinates_1[0] - 60, center_coordinates_1[1] + 20
fontScale              = 0.75
fontColor              = (0, 0, 0)
thickness              = 2

cv.putText(img,f'R = {radius_1}"', 
    bottomLeftCornerOfText, 
    font, 
    fontScale,
    fontColor,
    thickness,
          )

img = cv.circle(img, center_coordinates_1, radius_1, color, thickness)

#####################################
pt3 = center_coordinates_2[0] - radius_1
pt4 = center_coordinates_2[1]
img = cv.line(img, center_coordinates_2, (pt3, pt4), (255, 0, 0), 2)

font                   = cv.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = center_coordinates_2[0] - 60, center_coordinates_2[1] + 20
fontScale              = 0.75
fontColor              = (0, 0, 0)
thickness              = 2

cv.putText(img,f'R = {radius_2}"', 
    bottomLeftCornerOfText, 
    font, 
    fontScale,
    fontColor,
    thickness,
          )

img = cv.circle(img, center_coordinates_2, radius_2, color, thickness)

#####################################
pt1 = center_coordinates_1[0]
pt2 = center_coordinates_1[1] + radius_1 + 20

pt3 = center_coordinates_2[0]
pt4 = center_coordinates_2[1] + radius_2 + 20

img = cv.line(img, (pt1, pt2), (pt3, pt4), (255, 0, 0), 2)

font                   = cv.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (int((pt1+pt2)/3), pt2+25)
fontScale              = 0.75
fontColor              = (0, 0, 0)
thickness              = 2
# lineType               = 1

cv.putText(img,f'W = {length}"', 
    bottomLeftCornerOfText, 
    font, 
    fontScale,
    fontColor,
    thickness,
          )

#####################################3

offset = int(np.sin(np.pi/10) * (center_coordinates_2[1] - int(3*radius_2)))

head = (center_coordinates_2[0]-offset, center_coordinates_2[1] - int(3*radius_2))
img = cv.line(img, center_coordinates_2, head, color, thickness)

img = cv.line(img, head, center_coordinates_1, color, thickness)

head2 = head[0] - 100, head[1]
img = cv.line(img, head, head2, color, thickness)

plt.imshow(img)
plt.xticks([])
plt.yticks([])
plt.box(False)
st.pyplot()