
#----------------------------------------------------
def printConfigs(conf) :
    if type(conf) != type([]) :
        configs = [conf]
    else : configs = conf

    for config in configs :
        print 'Configuration:'
        for k in config.keys() :
            print '    key:',str(k).ljust(15),'value:',str(config[k]).ljust(20)

def hasAndIsTrue(config,thing) :
    return thing in config.keys() and config[thing]

#----------------------------------------------------
def getConfigItem(c,i) :
    if type(c) == type([]) :
        return c[i]
    else :
        return c

#----------------------------------------------------
def getDict(configStr,defaultsStr = '',ConfigFile='IsEMConfig') :

    MyConfig = dict()

    import_string = 'from '+ConfigFile+' import '+configStr+' as config'
    exec import_string

    if defaultsStr :
        defaults_string = 'from '+ConfigFile+' import '+defaultsStr+' as defaults'
        exec defaults_string
        for i in defaults.keys() :
            if i not in config.keys() :
                config[i] = defaults[i]
            
    return config

#----------------------------------------------------
def getConfig(configStr,index=0,defaultsStr = '',ConfigFile='IsEMConfig') :
    return getListOfConfigs(configStr,defaultsStr,ConfigFile)[index]

#----------------------------------------------------
def getListOfConfigs(configStr,defaultsStr = '',ConfigFile='IsEMConfig') :

    import_string = 'from '+ConfigFile+' import '+configStr+' as config'
    exec import_string
    if defaultsStr :
        defaults_string = 'from '+ConfigFile+' import '+defaultsStr+' as defaults'
        exec defaults_string
    else : defaults = 0

    return convertDictToList(config,defaults)

#----------------------------------------------------
# Convert a dictionary with lists in it to a list of flat dictionaries.
def convertDictToList(config,defaults=0) :

    MyConfigs = []

    # Get number of menus / dicts
    nindices = 1
    for i in config.keys() :
        if type(config[i]) == type([]) :
            if (nindices > 1) and (len(config[i]) != nindices) :
                print 'Config dictionary has varying list lengths! Your code will break.(',i,') (',nindices,')'
                if 'name' in config.keys(): print config['name']
            nindices = max(len(config[i]),nindices)

    # Fill menus / dicts
    for index in range(nindices) :
        tmpConfig = dict()
        for i in config.keys() :
            #if not getConfigItem(config[i],index) : continue
            tmpConfig[i] = getConfigItem(config[i],index)

        if defaults :
            for i in defaults.keys() :
                if i not in tmpConfig.keys() :
                    tmpConfig[i] = defaults[i]

        MyConfigs.append(tmpConfig)
        
    return MyConfigs
