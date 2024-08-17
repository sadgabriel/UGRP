#!/usr/bin/env node

const room_config = {
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
const yaml = require('js-yaml');

var roguelike = require(path.join(__dirname, "node-roguelike", "level", "roguelike"));

const file = fs.readFileSync('./config.yaml', 'utf8');
const config = yaml.load(file);

/**
 * Generates a random integer between two values, inclusive.
 *
 * The returned value will be between the provided `min` (inclusive) and `max` (inclusive).
 * If `min` or `max` are not integers, they will be rounded up or down, respectively, before
 * generating the random integer.
 *
 * @param {number} min - The minimum integer value (inclusive).
 * @param {number} max - The maximum integer value (inclusive).
 * @returns {number} A random integer between `min` and `max`, inclusive.
 */
function _getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Divides an array into smaller arrays (batches) of a specified size.
 *
 * The function splits the input `array` into sub-arrays, each with a length of `batchSize`.
 * The final batch may contain fewer elements if the original array's length is not a multiple of `batchSize`.
 *
 * @param {Array} array - The array to be divided into batches.
 * @param {number} batchSize - The number of elements each batch should contain.
 * @returns {Array<Array>} An array containing the divided batches. Each batch is an array of elements.
 */
function _divideArray(array, batchSize) {
  let result = [];
  for (let i = 0; i < array.length; i += batchSize) {
    let batch = array.slice(i, i + batchSize);
    result.push(batch);
  }
  return result;
}

/**
 * Converts a 2D array representing a game level into a string representation.
 *
 * The function takes a `level` object with a `world` property, which is a 2D array.
 * Each element in the `world` array represents a tile, and the function converts
 * these tiles into corresponding characters based on a `tileMapping` object.
 * The resulting string representation of the level is returned, with rows separated by newline characters.
 *
 * @param {Object} level - The level object containing the `world` property, a 2D array of tiles.
 * @param {Array<Array>} level.world - A 2D array representing the tiles in the game level.
 * @returns {string} A string representation of the game level, with each row separated by a newline character.
 */
function _convertToString(level){
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

/**
 * Creates a roguelike map with specified dimensions and room constraints.
 *
 * The function generates a game map based on the provided parameters for width, height,
 * and room size constraints. It utilizes the `roguelike` function to create the level,
 * and then converts the generated level into a string representation using `_convertToString`.
 * The function returns an object containing both the map parameters and the string representation
 * of the map.
 *
 * @param {number} width - The width of the map in tiles.
 * @param {number} height - The height of the map in tiles.
 * @param {number} roomMinWidth - The minimum width of the rooms in the map.
 * @param {number} roomMaxWidth - The maximum width of the rooms in the map.
 * @param {number} roomMinHeight - The minimum height of the rooms in the map.
 * @param {number} roomMaxHeight - The maximum height of the rooms in the map.
 * @param {number} roomIdeal - The ideal number of rooms in the map.
 * @param {number} retry - The number of retries allowed for generating the map.
 * @returns {Object} An object containing the map parameters and the string representation of the map.
 * @returns {Object.params} An object containing the input parameters used to generate the map.
 * @returns {string} map.map - A string representation of the generated map.
 */
function _createMap(width, height, roomMinWidth, roomMaxWidth, roomMinHeight, roomMaxHeight, roomIdeal, retry){

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

  let stringMap = _convertToString(level);

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

/**
 * Generates multiple roguelike maps based on a specified size and count.
 *
 * The function creates a series of maps, each with randomly determined dimensions 
 * within the specified configuration for the given `mapSize`. It attempts to generate 
 * the requested number of maps (`count`), but will stop early if too many errors occur during 
 * the map creation process. Each map is generated using the `_createMap` function.
 *
 * @param {string} mapSize - The size category of the maps to generate, used to fetch the corresponding configuration.
 * @param {number} count - The number of maps to generate.
 * @returns {Array<Object>} An array of map objects, where each object contains the parameters and string representation of the map.
 */
function createMaps(mapSize, count){
  let mapConfig = room_config[mapSize];
  let maps = [];

  let error_count = 0;
  for (let i = 0; i < count; i++){
    let width = _getRandomInt(mapConfig["map_min"], mapConfig["map_max"]);
    let height = _getRandomInt(mapConfig["map_min"], mapConfig["map_max"]);
    
    try {
      var map = _createMap(width, height, mapConfig["room_min"], mapConfig["room_max"], mapConfig["room_min"], mapConfig["room_max"], mapConfig["room_ideal"], mapConfig["retry"]);
    } catch {
      error_count++;
      if (error_count > 100){
        console.log("Too Many Errors occur.")
        return maps;
      }
      i--;
      continue;
    }

    map.size = mapSize
    maps.push(map);
  }

  return maps;
}

/**
 * Saves a list of maps to JSON files, divided into batches.
 *
 * This function takes an array of maps and splits it into batches of a specified size.
 * Each batch is then saved as a separate JSON file in a predefined directory. The files are named
 * using a specified prefix followed by the batch number. If the target directory does not exist,
 * it will be created.
 *
 * @param {Array<Object>} maps - An array of map objects to be saved.
 * @param {string} [prefix="batch"] - The prefix used for the names of the JSON files. Defaults to "batch".
 * @param {number} [batchSize=100] - The number of maps to include in each batch. Defaults to 100.
 */
function saveMaps(maps, prefix = "batch", batchSize = 100){
  batches = _divideArray(maps, batchSize);
  let directoryName = config["paths"]["raw"];

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

let smallMapNum = 100;
let largeMapNum = 100;

if (process.argv.length > 2){
  const args = process.argv.slice(2);
  smallMapNum = Number(args[0]);
  largeMapNum = Number(args[1]);
}

let smallMaps = createMaps("small", smallMapNum);
let largeMaps = createMaps("large", largeMapNum);
saveMaps(smallMaps.concat(largeMaps));