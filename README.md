# kk6gpv-api
<p align="center">
  <img src="https://github.com/areed145/kk6gpv-api/workflows/Heroku/badge.svg">
</p>
goal will be to re-create kk6gpv.net as a fast-api

## stack
- python
- mongodb
- flask
- boostrap
- plotly
- mapbox
- datashader (tbd)
- mqtt

## structure
- weather
    - aviation
    - station
    - blips
    - soundings
- iot
    - home assistant
    - vibration protocol
- aprs
    - prefix
    - entry
    - radius
- flying
    - aircraft
    - paragliding
    - sailplane
    - n5777v
- photos
    - travel
    - flickr gallery
- oil & gas
     - summary
     - maps

## todo
- styling
- optimize deployment
- metpy incorporation

## done
- move gallery listing to db
- details pages for APRS info
- CRM modeling for oil & gas
- UI
- rebuild flickr photo gallery functionality
- add old mongodb data (delete incorrect, load correct)
- move to kubernetes cluster
- incorporate fetchers
- incorporate Plotly.react in other plots
- port DOGGR data
- convert time queries to date range
- connect to mongodb
- live updating plots
- rebuild flickr gallery functionality
- add weather maps
- multi-services in kubernetes?
- add station weather plots
- move to local mongodb
- builder like blog for writing about projects
- figure out how to add raster layers to maps (leaflet? instaead of plotly for mapbox)
