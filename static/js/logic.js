// Add a tile layer.
var tile_Layer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

// Initialize all the LayerGroups that we'll use.
var layers = {
  ALL_RESIDENTIAL: new L.LayerGroup(),
  TOWNHOUSE: new L.LayerGroup(),
  CONDO_COOP: new L.LayerGroup(),
  MULTI_FAMILY: new L.LayerGroup(),
  SINGLE_FAMILY: new L.LayerGroup()
};

// Create a map object that centers on California.
var CaliMap = L.map("map", {
  center: [36.4783, -119.4179],
  zoom: 7,
  layers: [
    layers.ALL_RESIDENTIAL,
    layers.TOWNHOUSE,
    layers.CONDO_COOP,
    layers.MULTI_FAMILY,
    layers.SINGLE_FAMILY
  ]
});

tile_Layer.addTo(CaliMap);

  // Custom popup to the leaflet map (key findings)
  var popupSummary = L.popup({
    closeButton: false,
    autoClose: false,
    closeOnClick: false,
    minWidth: 600,
    maxWidth: 600,
    className: 'popupSummary'

  })
  .setLatLng([34.4783, -126.0179])
  .setContent('<h4><strong>Key Statistics 2021 vs 2020</strong> (Single-Family)</h4> <hr> <ul style="list-style-type:square"> <li>Top-3 counties with the greatest increase in values were Alameda($257k), Santa Clara($252k), and Marin($254k).</li> <br> <li>Top-3 counties with the greatest increase in percentages were Alpine(28%), Calaveras(26%), and Alameda(24%).</li> <br> <li>Mariposa was the only county that experienced a drop in housing price YoY (-$135k, -22%).</li></ul>')
  .openOn(CaliMap);

// Create an overlays object to add to the layer control (top-right of map).
var overlays = {
  "All Residential": layers.ALL_RESIDENTIAL,
  "Townhouse": layers.TOWNHOUSE,
  "Condo/Co-Op": layers.CONDO_COOP,
  "Multi-Family": layers.MULTI_FAMILY,
  "Single-Family": layers.SINGLE_FAMILY
};

// Create a control for our layers, and add our overlays to it.
L.control.layers(null, overlays).addTo(CaliMap);

// Adding Legend
var legend = L.control({position: 'bottomright'});

legend.onAdd = function () {
  var div = L.DomUtil.create('div','legend');
  return div;
};

// Add the legend to the map
legend.addTo(CaliMap);

// Create Icons Object for each property type
var icons = {
  ALL_RESIDENTIAL: L.ExtraMarkers.icon({
    icon: "ion-android-home",
    iconColor: "white",
    markerColor: "pink",
    shape: "penta"
  }),
  TOWNHOUSE: L.ExtraMarkers.icon({
    icon: "ion-ios-home-outline",
    iconColor: "white",
    markerColor: "red",
    shape: "circle"
  }),
  CONDO_COOP: L.ExtraMarkers.icon({
    icon: "ion-ios-home-outline",
    iconColor: "white",
    markerColor: "blue-dark",
    shape: "circle"
  }),
  MULTI_FAMILY: L.ExtraMarkers.icon({
    icon: "ion-ios-home",
    iconColor: "white",
    markerColor: "orange",
    shape: "circle"
  }),
  SINGLE_FAMILY: L.ExtraMarkers.icon({
    icon: "ion-ios-home",
    iconColor: "white",
    markerColor: "green",
    shape: "circle",
  })
};

// Define path for source data
var CaliHousing = "http://127.0.0.1:5000/ca_housing_data"

// Initialize housingType, which will be used as a key to access the appropriate layers and icons for the layer group.
var housingType;

// Call in and loop through the data to create markers for each counties.
d3.json(CaliHousing).then(function (data) {
  var yrsel = 2021;
  var year_ = data.filter(pax=>pax.Year==yrsel);
  var yrsel2 = 2020;
  var year_2 = data.filter(pax=>pax.Year==yrsel2);

  for (var i = 0; i < year_.length; i++) {
    let location = [year_[i].lat, year_[i].lng];
    let price = Math.round(year_[i].Median_sales_price);
    let countyName = year_[i].County;
    let type = year_[i].Property_type;
    let year = year_[i].Year;

    for (var j = 0; j < year_2.length; j++) {
      let countyName2 = year_2[j].County;
      let type2 = year_2[j].Property_type;

      if(countyName==countyName2 && type==type2){
        let price2 = Math.round(year_2[j].Median_sales_price);
        let priceYoY = (price-price2)/price2*100;

        if (type == "All Residential") {
          housingType = "ALL_RESIDENTIAL";
        }
        else if (type == "Condo/Co-op") {
          housingType = "CONDO_COOP";
        }
        else if (type == "Multi-Family (2-4 Unit)") {
          housingType = "MULTI_FAMILY";
        }
        else if (type == "Single Family Residential") {
          housingType = "SINGLE_FAMILY";
        }
        else {
          housingType = "TOWNHOUSE";
        }
    
        let newMarker = L.marker(location, {icon: icons[housingType]})
        .addTo(CaliMap);
     
        // Create Popup contents
        var customPopup = `<p>County Name: ${countyName}</p> <hr> 
        <p>Property Type: ${type}</p> <hr> <p>Avg. Median Sales Price: <br> $ 
        ${price.toLocaleString("en-US")} (YoY: ${priceYoY.toFixed()}%)</p> <hr> <p>Year: ${year}</p>`
    
        // Specify popup options
        var customOptions = 
        {
          'className': 'popupCustom'
        }
    
        // Add the new marker to the appropriate layer.
        newMarker.addTo(layers[housingType]);
    
        newMarker.bindPopup(customPopup,customOptions);
      }
    }
  };
  showLegend();
});

// Show the legend's innerHTML
function showLegend(){
  document.querySelector(".legend").innerHTML = [
    "<p class='property-type'>Property Types : </p>",
    "<hr>",
    "<p class='all-residential'>All Residential</p>",
    "<p class='townhouse'>Townhouse</p>",
    "<p class='condo-coop'>Condo/Co-op</p>",
    "<p class='multi-family'>Multi-Family</p>",
    "<p class='single-family'>Single-Family</p>"
  ].join("");
}

// END