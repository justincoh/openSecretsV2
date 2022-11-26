// import stuff from "./counties-albers-10m.json"

// const projection = d3.geoAlbersUsa().scale(1300).translate([487.5, 305])

const mapContainer = document.getElementById("map");
const width = mapContainer.clientWidth;
const height = mapContainer.clientHeight;

const getData = async () => {
  return await d3.json("https://cdn.jsdelivr.net/npm/us-atlas@3/counties-albers-10m.json");
}

const main = async () => {
  const data = await getData();
  const { features } = topojson.feature(data, data.objects.states);
  // const { features } = topojson.feature(data, data.objects.counties);
  console.log("fetched data");

  // const projection = d3.geoAlbersUsa()
  //   .scale(100)
  //   .translate([width / 2, height / 2]);

  const path = d3.geoPath(); //.projection(projection);
  const svg = d3.select("#map")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")

    svg.selectAll(".states")
      .data(features)
      .enter()
      .append("path")
      .attr("class", "state")
      .attr("d", path);
}

main();
