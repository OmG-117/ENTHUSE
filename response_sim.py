import sys
import time
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
matplotlib.use('TkAgg')

def responseCurve(t):
    return (thrustSettingActual*0.0104)*(0.0179*(t**5) - 0.4773*(t**4) + 4.0897*(t**3) - 11.2350*(t**2) + 10.8910*(t**1) + 2.4685*(t**0))

def nominalThrust(t):
    if t < 2:
        return responseCurve(2)
    elif t > 8.4:
        return responseCurve(8.4)
    else:
        return responseCurve(t)

plt.ion()
fig = plt.figure()
ax = plt.subplot(1,1,1)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Value (%)')
ax.set_xlim(left = 0, right = 9)
ax.set_ylim(bottom = 0, top = 150)
timeCoords = []
thrustCoords = []
nominalCoords = []
hydrogenCoords = []
ax.plot(timeCoords, thrustCoords, 'ko-', markersize = 1, color = 'green', label = 'Augmented Thrust')
ax.plot(timeCoords, nominalCoords, 'ko-', markersize = 1, color = 'blue', label = 'Typical Thrust')
ax.plot(timeCoords, hydrogenCoords, 'ko-', markersize = 1, color = 'red', label = 'Hydrogen Flow')
ax.legend(loc = 'upper left')
fig.show()

thrustSetting = input("Enter target thrust setting (%): ")
if thrustSetting == '':
    thrustSetting = 90.0
else:
    thrustSetting = float(thrustSetting)
if thrustSetting > 100.0:
    thrustSettingActual = 100.0
    thrustSetting = 125.0
else:
    thrustSettingActual = thrustSetting

pause = input("Press enter to start simulation.\n")
del pause

t = 0
hydrogenFlow = 0
previousFlow = 0
previousError = 0
previousTime = 0.001
integralSum = 0
startTime = time.time()

print("Simulation started.\n")
print("Throttle setting: {0}".format(str(thrustSetting)))

while t < 9:
    t = time.time() - startTime
    hydrogenThrust = 120*hydrogenFlow
    thrust = nominalThrust(t) + hydrogenThrust

    thrustError = thrustSetting - thrust
    hydrogenFlowTarget = 0.092*thrustError + 0.025*(thrustError - previousError)/(t - previousTime)

    flowError = hydrogenFlowTarget - hydrogenFlow
    hydrogenFlow += flowError*0.010 - 0.001*integralSum
    if hydrogenFlow > 1:
        hydrogenFlow = 1
    elif hydrogenFlow < 0:
        hydrogenFlow = 0

    integralSum += hydrogenFlow*(t - previousTime)
    if thrustSettingActual - (thrust - hydrogenThrust) < 20:
        integralSum *= 0.95

    previousFlow = hydrogenFlow
    previousError = thrustError
    previousTime = t

    timeCoords.append(t)
    thrustCoords.append(thrust)
    nominalCoords.append(nominalThrust(t))
    hydrogenCoords.append(hydrogenFlow*100)

    ax.lines[0].set_data(timeCoords, thrustCoords)
    ax.lines[1].set_data(timeCoords, nominalCoords)
    ax.lines[2].set_data(timeCoords, hydrogenCoords)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.flush_events()

    sys.stdout.write("\rThrust: {0}% | Hydrogen Flow: {2} ({3}) | Elapsed time: {1} s".format(round(thrust, 2), round(t, 2), round(hydrogenFlow, 2), round(hydrogenFlowTarget, 2)))

save = input("\n\nSave current figure? (Y): ")
if save.lower() == 'y':
    saveName = '{0}_{1}.png'.format(int(thrustSettingActual), int(time.time()))
    plt.savefig(saveName)
    print("Figure saved as \"{0}\".".format(saveName))
else:
    print("Figure not saved.")

pause = input("\nPress enter to exit.")
plt.close()
