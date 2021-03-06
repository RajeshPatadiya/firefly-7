#-------------------------------------------------------------------------------
# UI
filterModes = [
    'None',
    'Masses',
]

try:
    imagePath
except NameError:
    imagePath = "./"

# Omium is the web renderer. we use it to render the user interface
o = Omium.getInstance()

# start up the web server that will serve the user interface.
porthole.initialize(4080, './fireflyUi.html')
ps = porthole.getService()
ps.setServerStartedCommand('loadUi()')
ps.setConnectedCommand('onClientConnected()')

# used for passing boleans from the js interface
useSmoothingLength = False
true = True
false = False

# called when the user interface is ready. Create an overlay to display it.
def loadUi():
    global gui
    global p
    gui = Overlay()
    p = o.getPixels()
    guifx = OverlayEffect()
    guifx.setShaders('overlay/overlay.vert', 'overlay/overlay-flipy.frag')
    gui.setTexture(p)
    gui.setAutosize(True)
    gui.setEffect(guifx)
    o.setFocusChangedCommand('onUiFocusChanged()')
    o.open('http://localhost:4080')
    onResize()
    onUiFocusChanged()

def onUiFocusChanged():
    if(o.isFocused()):
        gui.setAlpha(1)
    else:
        gui.setAlpha(0.8)

# called when a user interface client connects.
def onClientConnected():
    initializePresetViews()
    ps.broadcastjs('initializePresetPanels()', '')
    #print "Color Map Names: " , colorMapNames
    ps.broadcastjs('initializeControls({0}, {1}, {2}, {3}, {4}, {5})'
        .format(dataModes, colorMapLabels, colorMapNames, filterModes, kernelModes, renderModes), '')
    o.setZoom(-1)
    updateJavaScriptInterface()

# handle input events
def onEvent():
    e = getEvent()
    if(e.isFlagSet(EventFlags.Ctrl)): enablePivotSelectorMode(True)
    elif(e.getType() == EventType.Up and not e.isFlagSet(EventFlags.Ctrl) and pivotSelectionMode) : enablePivotSelectorMode(False)

    if(e.isKeyDown(Keyboard.KEY_M)): ps.broadcastjs('toggleColorMap()','')
    if(e.isKeyDown(Keyboard.KEY_H)): ps.broadcastjs('toggleHelp()','')
    if(e.isKeyDown(Keyboard.KEY_V)): ps.broadcastjs('clearConsole()','')
    if(e.isKeyDown(Keyboard.KEY_C)): ps.broadcastjs('toggleConsole()','')
    
setEventFunction(onEvent)

def setKernelMode(mode):
    # pass the kernel mode index to the shaders and redraw
    global kernelModeInd
    print "Setting Kernel Mode to: " , mode
    kernelModeInd = mode
    for p in programs: p.define('KERNEL_MODE', str(mode))
    redraw()

def setRenderMode(mode):
    # pass the render mode index to the shaders and redraw
    print "Setting Render Mode to: ", mode
    global renderMode, renderModeInd
    renderMode = renderModes[mode]
    renderModeInd = mode
    for p in programs: p.define('RENDER_MODE', str(mode))
    redraw()
    
def enableColormapper(enabled):
    global colormapperEnabled
    print "setting colormapper enabler to: " , enabled
    colormapperEnabled = enabled
    pcw.enableColormapper(enabled)
    redraw()

def enableSmoothingLength(enabled):
    global useSmoothingLength
    print "setting smoothing length enabled to: " , enabled
    useSmoothingLength = enabled
    if(enabled):
        pc0.setSize(s0)
    else:
        pc0.setSize(None)
    redraw()
    
def setPointScale(sc):
    global pointScale
    pointScale = sc
    for p in parts: p.setPointScale(sc)
    print('point scale set to ' + str(sc))
    redraw()

def enableProgressive(sc):
    global progressiveRender
    progressiveRender = sc
    print "Setting Progressive to ", progressiveRender
    redraw()

def setDecimationValue(dc):
    global dqDec
    dqDec = int(dc)
    print "setting decimation value to ", dqDec
    redraw()
  
def setColormap(index):
    print "setting colormap to ",index
    global currentColorMapIndex
    currentColorMapIndex = index
    for p in parts: p.setColormap(colormaps[index])
    pcw.setColormap(colormaps[index])
    redraw()

def updateColormapBounds(cmin, cmax):
    print('bounds now are min: {0}  max:  {1}'.format(cmin, cmax))
    global colormapMin
    global colormapMax
    colormapMin = cmin
    colormapMax = cmax
    pcw.setChannelBounds(colormapMin, colormapMax)
    redraw()

def resetColormapBounds():
    print "resetting Colormap bounds"
    queueCommand('sendColormapBounds()')
    #pcw.updateChannelBounds(True)


def sendColormapBounds():
    global colormapMin
    global colormapMax
    colormapMin = pcw.getChannelMin()
    colormapMax = pcw.getChannelMax()
    ps.broadcastjs("updateColormapBounds({0}, {1})".format(colormapMin, colormapMax), '')

def setFilterMode(mode):
    global filterMode
    filterMode = mode
    dm = filterModes[mode]
    if(dm == 'None'): 
        for p in parts: p.setFilter(None)
    elif(dm == 'Density'): 
        pc0.setFilter(d0)
    redraw()

def updateFilterBounds(cmin, cmax):
    print('bounds now are {0}    {1}'.format(cmin, cmax))
    for p in parts: p.setFilterBounds(cmin, cmax)
    redraw()

def resetFilterBounds():
    print('resetting bounds')
    
    
def enableLogScale(enable):
    global isLogScale
    print "Setting log scale to: " , enable
    isLogScale = enable
    if(enable):
        for p in programs: p.define('LOG_MODE', '1')
    else:
        for p in programs: p.define('LOG_MODE', '0')
    global colormapMax, colormapMin
    updateColormapBounds(colormapMin,colormapMax)
    redraw()
    
def saveViewImage():
    global imagePath
    if not 'imagePath' in globals(): 
        imagePath = ""
    filename = '{:%Y%m%d-%H%M%S}.png'.format(datetime.datetime.now())
    filename = imagePath +  filename
    print "Saving Image to destination: ", filename
    saveImage(pcw.getOutput(), filename, ImageFormat.FormatPng)
    #ps.broadcastjs("setScreenView('{0}')".format(filename), '')
        
def echo(msg):
    ps.broadcastjs("setConsole('" + msg + "')", '')

def cls():
    ps.broadcastjs('clearConsole()', '')

def requestUpdatePos():
    global cameraPosition
    ps.broadcastjs('updateCameraPos('+str(cameraPosition[0])+','+str(cameraPosition[1])+','+str(cameraPosition[2])+')','')


def updateJavaScriptInterface():
    # print "Updating Python Interface"
    global dataMode,useSmoothingLength,isLogScale,pointScale,colormapperEnabled,currentColorMapIndex
    global colormapMin,colormapMax,cameraPosition,pivotPosition, renderModeInd, kernelModeInd
    ps.broadcastjs("postLoadUpdate({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15},{16},{17})"
        .format(dataMode, boolToJs(useSmoothingLength), boolToJs(isLogScale), pointScale,boolToJs(colormapperEnabled),currentColorMapIndex,colormapMin,colormapMax,cameraPosition[0],cameraPosition[1],cameraPosition[2],pivotPosition[0],pivotPosition[1],pivotPosition[2],renderModeInd,kernelModeInd,boolToJs(progressiveRender),dqDec), '')

def boolToJs(pythonBool):
    if pythonBool == False:
        return "false"
    else:
        return "true"
