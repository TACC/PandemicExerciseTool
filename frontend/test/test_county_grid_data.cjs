const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const context = {window: {}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../assets/county_data.js'), 'utf8'), context);
const {selectDay, selectedAge} = context.window.dash_clientside.countyData;
const plain = value => JSON.parse(JSON.stringify(value));

test('legacy custom expansion functions are inactive', () => {
    assert.equal(context.window.dash_clientside.countyData.updateRow, undefined);
    assert.equal(context.window.dash_clientside.countyData.ageContent, undefined);
});

test('day projection excludes age history and map boundaries', () => {
    const day = {day: 0, counties: [{fips: '48201', infected: 10, ageGroups: ['unused']}]};
    const output = selectDay([day], 0, {mapping: {Harris: '48201'}, geojson: 'unused'});
    assert.equal(output.counties[0].infected, 10);
    assert.equal(output.counties[0].ageGroups, undefined);
    assert.equal(output.geojson, undefined);
    assert.deepEqual(day.counties[0].ageGroups, ['unused']);
    assert.equal(selectDay([], 0, {}), null);
});

test('only selected county age groups leave the browser', () => {
    const ages = [{infected: 10}];
    const output = selectedAge([{'48201': ages, '48001': ['other county']}], 0, '48201');
    assert.deepEqual(plain(output), {fips: '48201', day: 0, pending: false, ages: ages});
    assert.equal(JSON.stringify(output).includes('other county'), false);
    assert.equal(selectedAge([], 0, null), null);
});

test('timeline and selection changes select the correct age data', () => {
    const history = [{'48201': [10], '48001': [20]}, {'48201': [30], '48001': [40]}];
    assert.deepEqual(plain(selectedAge(history, 1, '48201').ages), [30]);
    assert.deepEqual(plain(selectedAge(history, 1, '48001').ages), [40]);
    assert.equal(selectedAge(history, null, '48001'), null);
});

test('pending and unavailable are distinct', () => {
    assert.equal(selectedAge([], 0, '48201').pending, true);
    const unavailable = selectedAge([{'48201': null}], 0, '48201');
    assert.equal(unavailable.pending, false);
    assert.equal(unavailable.ages, null);
});

test('request size stays constant as history grows', () => {
    const day = {'48201': [10]};
    const short = selectedAge([day], 0, '48201');
    const long = selectedAge(Array(200).fill(day), 199, '48201');
    assert.deepEqual(plain(short.ages), plain(long.ages));
    assert.ok(JSON.stringify(long).length - JSON.stringify(short).length <= 2);
});
