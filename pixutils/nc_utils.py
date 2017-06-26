# Functions to manipulate NetCDF files
# Written by S Lavender, June 2017
# Version 1-0 09 June 17

# Examples: 
#    nc_attrs, nc_dims, nc_vars = nc_utils.ncdump(nc_fid)
#    nc_utils.plotxyz(lons,lats,zvals,title,cbarlabel,pngfile)


# Turn verb to True to print in verbose mode
def ncdump(nc_fid, verb=False):
#     ncdump outputs dimensions, variables and their attribute information.
#     The information is similar to that of NCAR's ncdump utility.
#     ncdump requires a valid instance of Dataset.
# 
#     Parameters
#     ----------
#     nc_fid : netCDF4.Dataset
#         A netCDF4 dateset object
#     verb : Boolean
#         whether or not nc_attrs, nc_dims, and nc_vars are printed
# 
#     Returns
#     -------
#     nc_attrs : list
#         A Python list of the NetCDF file global attributes
#     nc_dims : list
#         A Python list of the NetCDF file dimensions
#     nc_vars : list
#         A Python list of the NetCDF file variables
###
    def print_ncattr(key):

#       Prints the NetCDF file attributes for a given key
# 
#       Parameters
#       ----------
#       key : unicode
#           a valid netCDF4.Dataset.variables key
        try:
            print("\t\ttype:", repr(nc_fid.variables[key].dtype))
            for ncattr in nc_fid.variables[key].ncattrs():
                print('\t\t%s:' % ncattr,\
                      repr(nc_fid.variables[key].getncattr(ncattr)))
        except KeyError:
            print("\t\tWARNING: %s does not contain variable attributes",key)

   # NetCDF global attributes
    nc_attrs = nc_fid.ncattrs()
    if verb:
        print("NetCDF Global Attributes:")
        for nc_attr in nc_attrs:
            print('\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr)))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        print("NetCDF dimension information:")
        for dim in nc_dims:
            print("\tName:", dim) 
            print("\t\tsize:", len(nc_fid.dimensions[dim]))
            print_ncattr(dim)
    # Variable information.
    nc_vars = [var for var in nc_fid.variables]  # list of nc variables
    if verb:
        print("NetCDF variable information:")
        for var in nc_vars:
            if var not in nc_dims:
                print('\tName:', var)
                print("\t\tdimensions:", nc_fid.variables[var].dimensions)
                print("\t\tsize:", nc_fid.variables[var].size)
                print_ncattr(var)
    return nc_attrs, nc_dims, nc_vars

def plotxyz(lons,lats,zvals,title,cbarlabel,pngfile):
      # Plot of parameter
      fig = plt.figure()
      fig.subplots_adjust(left=0., right=1., bottom=0., top=0.9)

      # Setup the map. http://matplotlib.org/basemap/users/mapsetup.html
      m = Basemap(projection='moll', llcrnrlat=-90, urcrnrlat=90,\
                  llcrnrlon=0, urcrnrlon=360, resolution='c', lon_0=0)
      m.drawcoastlines()
      m.drawcountries(color='coral')
      m.drawrivers(color='aqua')
      m.drawmapboundary()

      # Transforms lat/lon into plotting coordinates for projection
      x, y = m(lons, lats)

      # Plot with differernt colour palettes
      alpha = 1
      plt.scatter(x, y, c = zvals, cmap=plt.cm.jet)

      # Add title
      plt.title("\n".join(wrap(title,50)),multialignment='center')

      # warp around the colourbar title if it's long
      cbar = plt.colorbar(orientation='horizontal', shrink=0.75, pad=0.04)
      cbar.set_label("\n".join(wrap(cbarlabel,50)),multialignment='center', labelpad=0)

      # Save plot to PNG file
      plt.plot()
      plt.savefig(pngfile, bbox_inches='tight')
      print("Saved plot to: ",pngfile)

      # Clear out the plot
      plt.close()
