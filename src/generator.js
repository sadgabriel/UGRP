#!/usr/bin/env node

const config = {
  "small": {
    "map_min": 9,
    "map_max": 16,
    "room_min": 2,
    "room_max": 7,
    "room_ideal": 100,
    "retry": 100
  },
  "large": {
    "map_min": 16,
    "map_max": 30,
    "room_min": 3,
    "room_max": 9,
    "room_ideal": 100,
    "retry": 100
  }
}

const tileMapping = {
  0: ' ',
  1: '.',
  2: '#',
  3: '/',
  4: 'X',
  5: '<',
  6: '>'
};

const fs = require('fs')
const path = require('path')
var roguelike = require(path.join(__dirname, "node-roguelike", "level", "roguelike"));

function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function divideArray(array, batchSize) {
  let result = [];
  for (let i = 0; i < array.length; i += batchSize) {
    let batch = array.slice(i, i + batchSize);
    result.push(batch);
  }
  return result;
}

function convertToString(level){
  let world = level.world;

  let stringMap = "";

  for (let y = 0; y < world.length; y++) {
    let row = '';
    for (let x = 0; x < world[y].length; x++) {
      let tile = world[y][x];
      row += tileMapping[tile] || tile;
    }
    stringMap += row + '\n';
  }

  return stringMap;
}

function createMap(width, height, roomMinWidth, roomMaxWidth, roomMinHeight, roomMaxHeight, roomIdeal, retry){

  let level = roguelike({
    width: width,
    height: height,
    retry: retry,
    special: false,
    room: {
      ideal: roomIdeal,
      min_width: roomMinWidth,
      max_width: roomMaxWidth,
      min_height: roomMinHeight,
      max_height: roomMaxHeight
    }
  });

  let stringMap = convertToString(level);

  let map = {
    params: {
      map_width: width,
      map_height: height,
      retry: retry,
      room_ideal: roomIdeal,
      room_min_width: roomMinWidth,
      room_max_width: roomMaxWidth,
      room_min_height: roomMinHeight,
      room_max_height: roomMaxHeight
    },
    map: stringMap
  }

  return map;
}

function createMaps(mapSize, count){
  let mapConfig = config[mapSize];
  let maps = [];

  let error_count = 0;
  for (let i = 0; i < count; i++){
    let width = getRandomInt(mapConfig["map_min"], mapConfig["map_max"]);
    let height = getRandomInt(mapConfig["map_min"], mapConfig["map_max"]);
    
    try {
      var map = createMap(width, height, mapConfig["room_min"], mapConfig["room_max"], mapConfig["room_min"], mapConfig["room_max"], mapConfig["room_ideal"], mapConfig["retry"]);
    } catch {
      error_count++;
      if (error_count > 100){
        console.log("Too Many Errors occur.")
        return maps;
      }
      i--;
      continue;
    }

    maps.push(map);
  }

  return maps;
}

function saveMaps(maps, prefix = "batch", batchSize = 100){
  batches = divideArray(maps, batchSize);
  let directoryName = path.join(path.dirname(__dirname), "data", "1. raw");

  if (!fs.existsSync(directoryName)) {
    fs.mkdirSync(directoryName, { recursive: true });
  }
  
  for (let i = 0; i < batches.length; i++){
    let jsonData =  JSON.stringify({"map_list": batches[i]}, null, 4);
    fs.writeFile(path.join(directoryName, `${prefix}${i}.json`), jsonData, (err) => {
      if (err) {
        console.error('An error occurred:', err);
        return;
      }
    });
  }
}

let smallMaps = createMaps("small", 100);
let largeMaps = createMaps("large", 100);
saveMaps(smallMaps.concat(largeMaps));