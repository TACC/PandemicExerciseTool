const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = {window: {}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../assets/incremental_map.js'), 'utf8'), context);
const select = context.window.dash_clientside.incrementalMap.selectFrame;
const metadata = {state: 'Texas', fips: ['48001', '48003'], names: ['Anderson', 'Andrews']};
const day = {day: 7, counties: [
    {fips: '003', infected: 20, infectedPercent: 2, deceased: 1},
    {fips: '48001', infected: 10, infectedPercent: 1, deceased: 0, ageGroups: ['unused']}
]};
const plain = value => JSON.parse(JSON.stringify(value));

test('county order follows map locations, with counts and hover values aligned', () => {
    const frame = select([day], 0, 'count', null, metadata, 'Texas', {});
    assert.deepEqual(plain(frame.values), [10, 20]);
    assert.deepEqual(plain(frame.customdata), [['Anderson', 10, 1, 0], ['Andrews', 20, 2, 1]]);
    assert.equal(frame.day, 7);
    assert.equal(JSON.stringify(frame).includes('ageGroups'), false);
});

test('percentage mode and missing counties use explicit zero values', () => {
    const frame = select([{day: 1, counties: day.counties.slice(1)}], 0, 'percent', null, metadata, 'Texas', {});
    assert.deepEqual(plain(frame.values), [1, 0]);
    assert.deepEqual(plain(frame.customdata[1]), ['Andrews', 0, 0, 0]);
    assert.deepEqual(plain(select([], 0, 'count', null, metadata, 'Texas', {}).values), [0, 0]);
});

test('state transitions wait for matching map initialization', () => {
    assert.equal(select([day], 0, 'count', null, metadata, 'Delaware', {}), null);
    assert.equal(select([day], 0, 'count', null, null, 'Texas', {}), null);
});

test('selected polygon rings are separated and clearing selection removes lines', () => {
    const assets = {geojson: {features: [{properties: {GEOID: '48001'}, geometry: {
        type: 'MultiPolygon', coordinates: [[[[1, 2], [3, 4]]], [[[5, 6], [7, 8]]]]
    }}]}};
    const frame = select([day], 0, 'count', '48001', metadata, 'Texas', assets);
    assert.deepEqual(plain(frame.highlight.lon), [1, 3, null, 5, 7]);
    assert.deepEqual(plain(frame.highlight.lat), [2, 4, null, 6, 8]);
    assert.deepEqual(plain(select([day], 0, 'count', null, metadata, 'Texas', assets).highlight.lon), []);
    assert.equal(JSON.stringify(frame).includes('geojson'), false);
});

test('request size stays constant as simulation history grows', () => {
    const short = select([day], 0, 'count', null, metadata, 'Texas', {});
    const long = select(Array(200).fill(day), 199, 'count', null, metadata, 'Texas', {});
    assert.equal(JSON.stringify(short), JSON.stringify(long));
});
