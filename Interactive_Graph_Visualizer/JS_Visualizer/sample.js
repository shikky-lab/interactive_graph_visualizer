﻿
var width = 960,
    height = 500,
    k = 80;

var x = d3.scale.linear()
    .domain([0, width])
    .range([0, width]);

var y = d3.scale.linear()
    .domain([0, height])
    .range([0, height]);

var random = d3.random.normal(0, width);

var zoom = d3.behavior.zoom()
    .x(x)
    .y(y)
    .size([width, height])
    .on("zoom", zoomed);

var canvas = d3.select("body").append("canvas")
    .attr("width", width)
    .attr("height", height);

var context = canvas.node().getContext("2d");

context.fillStyle = "#ccc";
context.strokeStyle = "#fff";

canvas.call(zoom.event);

jump();

function zoomed() {
  context.fillRect(0, 0, width, height);
  context.lineWidth = 4 * zoom.scale();

  for (var d = x.domain(),
      x0 = Math.floor(d[0] / k) * k,
      x1 = Math.ceil(d[1] / k) * k; x0 <= x1; x0 += k) {
    context.beginPath();
    context.moveTo(x(x0), 0);
    context.lineTo(x(x0), height);
    context.stroke();
  }

  for (var d = y.domain(),
      y0 = Math.floor(d[0] / k) * k,
      y1 = Math.ceil(d[1] / k) * k; y0 <= y1; y0 += k) {
    context.beginPath();
    context.moveTo(0, y(y0));
    context.lineTo(width, y(y0));
    context.stroke();
  }
}

function jump() {
  canvas.transition()
      .duration(5000)
      .call(zoom.translate([random(), random()]).event)
      .each("end", jump);
}
