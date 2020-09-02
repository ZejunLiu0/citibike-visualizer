<template>
  <div id="app" class="container-fluid" style="margin:20px; height:100%">
    <div class="row" style="padding-left:15px">
      <div class="col-sm-4">
         <h3>Jersey City Citi Bike Trip Histories</h3>
         <h6>From 2016-09 to 2019-09</h6>
      </div>
      <div class="col-sm-5">
        <p><b>Question: {{ currentQuestion }}</b></p>
        <!-- <p>Question</p> -->
        <div class="input-group">
          <input type="text" class="form-control" placeholder="Your answer" v-model="answer" aria-label="Username" aria-describedby="basic-addon1">
          <div class="input-group-append" id="button-addon4">
            <button class="btn btn-secondary" type="button" v-on:click="nextQues">Next</button>
          </div>
        </div>
      </div>

      <div class="col-sm-1">
          <div style="padding:2px 10px" >
            <button type="button" class="btn btn-dark btn-sm" v-on:click="startWarmup">Start Warmup</button>          
          </div>
          <div style="padding:2px 10px" >
            <button type="button" class="btn btn-dark btn-sm" v-on:click="endWarmup">End Warmup</button>
          </div>         
      </div>
    </div> 
    <hr>
    <div class="row">

      <div class="col-sm-4">
        <div style="margin-bottom:5px" class="text-center">
          <p style="float:left"> Station: {{ this.stationSelected }} </p>
          <button type="button" class="btn btn-dark btn-sm" v-on:click="cleanStation">Reset station</button>          
        </div>

        <mapbox id="map"
          access-token="pk.eyJ1IjoiYXNzaWdubWVudDMiLCJhIjoiY2sxczVqMmlyMDVicDNvbHdocTk5Z3RvdSJ9.RG6qndYPwnzTCYQVlIbxJQ"
          :map-options="{
            style: 'mapbox://styles/mapbox/streets-v9',
            center: [-74.076661, 40.717651],
            zoom: 12,
            
          }"
          :geolocate-control="{
            show: true,
            position: 'top-left',
          }"
          @map-load="loaded"
          @map-zoomend="zoomend"
          @map-click:points="clicked"
          @geolocate-error="geolocateError"
          @geolocate-geolocate="geolocate"
        />
      </div>
      
      <div class="col-sm-3 text-center">
        <div style="margin-bottom:10px">
          Date Selector    
          <button type="button" class="btn btn-dark btn-sm" v-on:click="getMonth">Reset dates</button>          
        </div>

        <div>
          <!-- <calendar v-model="curr" v-on:dateSelected="dateSelected"/> -->
          <FunctionalCalendar
                v-model="calendarData"
                :configs="calendarConfigs"
                :newCurrentDate="curr"
                @choseDay="choseDay"
                @changedMonth="changedMonth"
                ref="calendar"
                v-on:pickMonth="monthPicked"
                v-on:pickYear="yearPicked"
                @changedYear="changedYear"
          ></FunctionalCalendar>
        </div>

      </div>

      <div id="dashboard_div" class="col-sm-4 text-center" >
        <h6>Age Distribution of Citibike Users (Filtering Hours) </h6>
        <div style="height:50px">
          <vue-slider 
          v-model="sliderValue"
          :adsorb="true"
          :marks="true"
          :data="data"
          @drag-end="dragEnd"
          ></vue-slider>
        </div>
        
        <div style="padding-left:20px" class="card">
          <VueApexCharts type=donut width=380 :options="chartOptions" :series="series" />
        </div>
      </div>
    </div>

    <div class="row" style="margin-top:20px">
          <VueApexCharts class="card" type=bar height=270 width=330 :options="barChartOptions" :series="barSeries" />
          <VueApexCharts class="card" type=bar height=270 width=530 style="margin: 0 2px" :options="distributionOptions" :series="distributionSeries" />
          <VueApexCharts class="card" type=line height=260 width=520 style="margin: 0 2px" :options="durationOptions" :series="durationSeries" />
    </div>
    </div>   
  </div>
</template>

<script>
import Mapbox from 'mapbox-gl-vue'
import format from 'date-fns/format'
import PopupContent from './components/PopupContent.vue'
import axios from 'axios';
import { FunctionalCalendar } from 'vue-functional-calendar';
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'
import VueApexCharts from 'vue-apexcharts'

let mapRef = {}
export default {
  name: 'app',
  components: { 
    Mapbox,
    FunctionalCalendar,
    VueSlider,
    VueApexCharts
   },
   data() {
    return {
      sliderValue: ['0', '24'],
      data: ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'],
      questions: [
        '1. What age range uses citibike the most?',
        '2. Which day has the largest total number of trips in February 2018?',
        '3. In January 2017, at the top 1 start station, which day has the largest average trip duration?',
        '4. In January 2017, which hour is the busiest hour in Tuesdays? ',
        '5. What are the total number of trips and the average trip duration of the hour you get in Q4?',
        '6. Which station is the nearest station to Grove St PATH? '
      ],
      currentQuestion: '',
      quesIndex: 0,
      answer: '',

      series: [],
      labels: [],

      // top stations
      barSeries: [{
          name: "Total",
          data: []
        }],
      barLabels: [],

      // distribution
      distributionSeries: [{
        name: "Total",
        type: "column",
        data: []
      }],
      distributionLabels: [],

      durationSeries: [{
          name: "Minutes",
          data: []
      }],
      durationLabels: [],

      calendarData: {},

      calendarConfigs: {
          // newCurrentDate: new Date(2016,9,1),
          markedDates: [],
          sundayStart: true,
          dateFormat: 'dd/mm/yyyy',
          isDateRange: false,
          // isDatePicker: true,
          isMultipleDatePicker: true,
          limits: {min: '01/09/2016', max: '30/09/2019'},
          // disabledDates:['24/12/2018','27/12/2018'],
          changeYearFunction: true,
          changeMonthFunction: true
      },
      yearSelected: '',
      monthSelected: '',
      dateMarked: ['2016-09'],
      curr: new Date(2016,8,1),
      currentMonthOrDate: '2016-09',
      stationSelected: null,
      title: 'Top 10 Start Station',
      bounds: [
        [-74.127821, 40.667509], // southwest
        [-73.984960, 40.775828 ]  // northeast
      ],
      popup: null,
      popupContent: null,
      feature_list: [],
      stops: [],
      tripDistribution: [],
      avgTripDur: [],
      topStations: {},
      age: [],
    };
  },

  created () {
    this.yearSelected = '2016';
    this.monthSelected = '09';
    this.dateMarked = ['2016-09']
    this.getStops();
    var dateAndStop = {
        'date': '2016-09',
        'stop': this.stationSelected,
        'hour': this.sliderValue

      };
    this.updateInfo(dateAndStop)
    console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Created.")
  },

  computed: {
    formattedMonth() {
      return format(this.curr, 'MM/YYYY');
    },
    formattedDate() {
      return format(this.curr, 'MM/DD/YYYY');
    },

    chartOptions() {
        return {
          labels: this.labels,
          responsive: [{
            breakpoint: 480,
            options: {
              chart: {
                width: 200
              },
              legend: {
                position: 'bottom'
              }
            }
          }]
        }
      },

      barChartOptions() {
        return {
          plotOptions: {
            bar: {
              horizontal: true,
            }
          },
          dataLabels: {
            enabled: false
          },
          xaxis: {
            categories: this.barLabels
          },
          title: {
              text: this.title,
              align: 'center',
              floating: true
          },
          chart: {
            events: {
              click: (event, chartContext, config) => {
                var date;
                if (this.dateMarked[0].length == 7)  
                  date = this.dateMarked[0]
                else  date = this.dateMarked
                this.stationSelected = this.barLabels[config.dataPointIndex];
                console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), 'Bar chart clicked: ', this.title, this.stationSelected)

                var dateAndStop = {
                    'date': date,
                    'stop': this.stationSelected,
                    'hour': this.sliderValue
                };
                this.updateInfo(dateAndStop)
                for (var i in this.stops ) {
                  if (this.stops[i].stopname == this.stationSelected) {
                    mapRef.flyTo({
                      center: [ this.stops[i].longitude, this.stops[i].latitude],
                        zoom: 16
                      })
                  }
                }
              },

              dataPointMouseEnter: (event, chartContext, config) => {
                console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), 'Mouse entered bar chart stop:',this.stops[config.dataPointIndex].stopname)
              }
            }
          }
        }
      },

      distributionOptions() {
        return {
          plotOptions: {
            bar: {
              horizontal: false,
              columnWidth: '60%',
              endingShape: 'rounded'	
            },
          },
          title: {
            text: 'Total Number of Trips',
            align: 'center',
            floating: true
          },
          dataLabels: {
            enabled: false
          },
          stroke: {
            show: true,
            width: 2,
            colors: ['transparent']
          },

          xaxis: {
            categories: this.distributionLabels,
            title: {
              text: 'Dates in a Month or Hours in a Day'
            }
          },
          fill: {
            opacity: 1

          },
          tooltip: {
            y: {
              formatter: function (val) {
                return val
              }
            }
          },
          chart: {
            events: {
              dataPointMouseEnter: (event, chartContext, config) => {
                console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), 'Mouse entered:', this.distributionLabels[config.dataPointIndex])
              }
            }
          }
        }
      },

      durationOptions() {
        return {
          chart: {
              zoom: {
                  enabled: false
              },
          },
          title: {
              text: 'Average Trip Duration in a Day/Month in Minutes',
              align: 'center',
              floating: true
          },
          dataLabels: {
              enabled: false
          },
          stroke: {
              curve: 'straight'
          },
          grid: {
              row: {
                  colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
                  opacity: 0.5
              },
          },
          xaxis: {
              categories: this.durationLabels,
          },
        }
      }
  },
  methods: {
    startWarmup() {
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Warmup starts ")
    },

    endWarmup() {
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Warmup ends ")
      this.currentQuestion = this.questions[0];
      this.quesIndex += 1;
    },

    nextQues() {
      if (this.quesIndex>6) {
        alert("Finished!")
        console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Finished!")
      }
      if (this.quesIndex==0) return
      this.currentQuestion = this.questions[this.quesIndex];
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Answered question", this.quesIndex, ':', this.answer)
      this.quesIndex += 1;
      this.answer=''
    },

    dragEnd() {
      var date
      if (this.dateMarked[0].length == 7)  
        date = this.dateMarked[0]
      else  date = this.dateMarked
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Slider dragged. Hours selected: ", this.sliderValue)

      var dateAndStop = {
          'date': date,
          'stop': this.stationSelected,
          'hour': this.sliderValue
      };
      this.updateInfo(dateAndStop)
    },

    monthPicked(key) {
      key = key+1;
      var month = key.toString().padStart(2, '0');
      this.monthSelected = month;
      this.dateMarked = [this.yearSelected+'-'+month]

      this.currentMonthOrDate = this.yearSelected+'-'+this.monthSelected
      this.calendarData.selectedDates = []
      var dateAndStop = {
          'date': this.yearSelected+'-'+this.monthSelected,
          'stop': this.stationSelected,
          'hour': this.sliderValue
      };
      this.updateInfo(dateAndStop)
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Month picked from month picker: ", this.dateMarked)


    },
    yearPicked(year) {
      this.yearSelected = year;
      this.dateMarked = [year+'-'+this.monthSelected]
      this.currentMonthOrDate = this.yearSelected+'-'+this.monthSelected
      this.calendarData.selectedDates = []
      var dateAndStop = {
          'date': this.yearSelected+'-'+this.monthSelected,
          'stop': this.stationSelected,
          'hour': this.sliderValue
      };
      this.updateInfo(dateAndStop)
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Year picked from year picker: ", this.dateMarked)

    },
    changedMonth(month) {
      var date = format(month, 'YYYY-MM');
      this.dateMarked = [date]
      this.currentMonthOrDate = date

      this.monthSelected = format(month, 'MM');
      this.yearSelected = format(month, 'YYYY');
      this.calendarData.selectedDates = []
      var dateAndStop = {
          'date': date,
          'stop': this.stationSelected,
          'hour': this.sliderValue
      };
      this.updateInfo(dateAndStop)
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Month changed: ", this.dateMarked)


    },
    changedYear(year) {
      this.yearSelected = format(year, 'YYYY');
      var month = format(year, 'YYYY-MM');
      this.dateMarked = [month]
      this.currentMonthOrDate = month

      this.calendarData.selectedDates = []
      var dateAndStop = {
          'date': this.yearSelected+'-'+this.monthSelected,
          'stop': this.stationSelected,
          'hour': this.sliderValue
      };
      this.updateInfo(dateAndStop)
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), "Year changed: ", this.dateMarked)


    },
    choseDay(day) {
      var month = day.date.split('/')[2]+'-'+day.date.split('/')[1].padStart(2, '0')
      if (this.dateMarked.includes(month)) {
          const items = this.dateMarked
          this.dateMarked = items.filter(item => item !== month)
      }
        if (this.dateMarked.includes(day.date)) {
          // console.log('include',this.dateMarked)
          if (this.dateMarked.length == 1) {
            var str = day.date;
            this.dateMarked = [str.split('/')[2]+'-'+str.split('/')[1].padStart(2, '0')]
            var dateAndStop = {
              'date': str.split('/')[2]+'-'+str.split('/')[1].padStart(2, '0'),
              'stop': this.stationSelected,
              'hour': this.sliderValue

            };
            this.updateInfo(dateAndStop)
            console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), day.date, "Unselected. Marked dates: ", this.dateMarked)

            return
          }

          const items = this.dateMarked
          this.dateMarked = items.filter(item => item !== day.date)
          console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), day.date, "Unselected. Marked dates: ", this.dateMarked)
        }
        else {
          this.dateMarked.push(day.date)
          console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), day.date, "Selected. Marked dates: ", this.dateMarked)
        }

        var dateAndStop = {
          'date': this.dateMarked,
          'stop': this.stationSelected,
          'hour': this.sliderValue
        };
        this.updateInfo(dateAndStop)
    },

    updateInfo(dateAndStop) {
      const path = 'http://localhost:5000/dateAndStop';
      axios.post(path, dateAndStop)
        .then((res) => {
          if (res.data['topStations']['name'].length==0 || res.data['tripDistribution']['name'].length==0  || res.data['avgTripDur']['name'].length==0 || res.data['age'].length==1 ){
            alert('No data:\nDate:'+this.dateMarked+'\nStation: '+this.stationSelected)
            console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'),'No data fetched. Date: '+this.dateMarked+' Station: '+this.stationSelected)
          }
          else {
            this.topStations = res.data['topStations'];
            this.avgTripDur = res.data['avgTripDur'];
            this.age = res.data['age'];

            this.labels = this.age.age;
            this.series = this.age.total;

            this.barSeries = [{name:"Total", data:res.data['topStations']['total']}]
            this.barLabels = res.data['topStations']['name']

            this.distributionSeries = [
              {
                name: "Total", 
                type: 'column',
                data:res.data['tripDistribution']['total']
              },
            ]
            this.distributionLabels = res.data['tripDistribution']['name']

            this.durationLabels = res.data['avgTripDur']['name']
            this.durationSeries = [{
                name: "Minutes",
                data: res.data['avgTripDur']['avg']
            }]

          }
        })
        .catch((error) => {
          console.log(error);
        });
    },

    getStops() {
      const path = 'http://localhost:5000/stops';
      axios.get(path)
      .then((res) => {
        this.stops = res.data;
        // console.log(res.data);
      })
      .catch((error) => {
        console.error(error);
      });
    },


// POST needed

    getMonth () {
      this.calendarData.selectedDates = [];
      this.calendarConfigs.markedDates = [];

      this.currentMonthOrDate = this.yearSelected+'-'+this.monthSelected
      this.dateMarked = [this.yearSelected+'-'+this.monthSelected]

      var dateAndStop = {
        'date': this.yearSelected+'-'+this.monthSelected,
        'stop': this.stationSelected,
        'hour': this.sliderValue
      };
      this.updateInfo(dateAndStop)
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), 'Month reset. Marked dates: ', this.dateMarked)

    },

    cleanStation () {
      mapRef.flyTo({
        center: [-74.076661, 40.717651],
        zoom: 12,
      })
      this.title = 'Top 10 Start Station'
      this.stationSelected=null;

      var date
      if (this.dateMarked[0].length == 7)  
        date = this.dateMarked[0]
      else  date = this.dateMarked
      
      var dateAndStop = {
        'date': date,
        'stop': this.stationSelected,
        'hour': this.sliderValue

      };
      this.updateInfo(dateAndStop)
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), 'Station reset.')

    },

    clicked(map, e) {
      mapRef.flyTo({
      center: [ e.lngLat.lng, e.lngLat.lat],
        zoom: 15
      })
        const title = e.features[0].properties.title
        this.stationSelected = title
        this.title = 'Number of records at ' + this.stationSelected
        var date
      if (this.dateMarked[0].length == 7)  
        date = this.dateMarked[0]
      else  date = this.dateMarked
      
      var dateAndStop = {
        'date': date,
        'stop': this.stationSelected,
        'hour': this.sliderValue
      };
      this.updateInfo(dateAndStop)
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'), 'Station in map selected: ', this.stationSelected)

    },

// POST needed end
    loaded(map) {
      mapRef = map;
      var feature_list = [];
      for (var d of this.stops){
        this.feature_list.push({
                          "type": "Feature",
                          "geometry": {
                              "type": "Point",
                              "coordinates": [d['longitude'], d['latitude']]
                          },
                          "properties": {
                            "title": d['stopname'],
                            "icon": "bicycle-share",
                            "description": d['id'],
                          }});
      }

      map.addLayer({
        id: 'points',
        type: 'symbol',
        source: {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: this.feature_list,
          },
        },
        layout: {
          'icon-size': 1.5,
          'icon-image': '{icon}-15',
          'text-field': '{title}',
          'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
          'text-offset': [0, 0.6],
          'text-anchor': 'top',
        },
        paint: {
                    'icon-color': "#00ff00",
                    "icon-halo-color": "#fff",
                    "icon-halo-width": 2
                }
      })

      var popup = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false
      });

      map.on('mouseenter', 'points', function(e) {
      // Change the cursor style as a UI indicator.
        map.getCanvas().style.cursor = 'pointer';

        var coordinates = e.features[0].geometry.coordinates.slice();
        var description = e.features[0].properties.description;
        
        // Ensure that if the map is zoomed out such that multiple
        // copies of the feature are visible, the popup appears
        // over the copy being pointed to.
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
        coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }
        
        // Populate the popup and set its coordinates
        // based on the feature found.
        popup.setLngLat(coordinates)
        .setHTML('Station ID: '+description)
        .addTo(map);
        
    });
      
    map.on('mouseleave', 'points', function() {
      map.getCanvas().style.cursor = '';
      popup.remove();
      });
    },

    zoomend(map, e) {
      console.log(format(new Date(), 'YYYY-MM-DD HH:mm:ss'),'Map zoomed')
    },
    
    geolocateError(control, positionError) {
      console.log("error")
      console.log(positionError)
    },
    geolocate(control, position) {
      console.log(
        `User position: ${position.coords.latitude}, ${position.coords.longitude}`
      )
    },
  },
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* text-align: center; */
  color: #2c3e50;
  /* margin-top: 60px; */
  width: 100%;
  height: 100%;
  position: relative;
}

#map {
  width: 100%;
  height: 320px;
}


</style>