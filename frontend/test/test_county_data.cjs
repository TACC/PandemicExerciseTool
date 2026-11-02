// LEGACY custom-expansion tests; preserved for rollback.
// // Run with: node --test test/test_county_data.cjs
// const {test} = require('node:test');
// const assert = require('node:assert/strict');
// const fs = require('node:fs');
// const vm = require('node:vm');
// const path = require('node:path');
// const noUpdate = {noUpdate: true};
// const context = {window: {dash_clientside: {no_update: noUpdate, callback_context: {}}}};
// vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../assets/county_data.js'), 'utf8'), context);
// const {selectDay, updateRow, ageContent} = context.window.dash_clientside.countyData;
// const ages = [{infected: 10}, {infected: 20}];
// const day = {day: 0, counties: [{fips: '01001', infected: 30, ageGroups: ages}, {fips: '01003', infected: 50}]};
// const assets = {mapping: {Autauga: '01001'}, geojson: {large: 'unused'}};
// const plain = value => JSON.parse(JSON.stringify(value));
// 
// test('table projection excludes all age details and map polygons', () => {
//     const output = selectDay([day], 0, assets);
//     assert.equal(output.counties[0].ageGroups, undefined);
//     assert.equal(output.counties[0].infected, 30);
//     assert.equal(output.geojson, undefined);
//     assert.deepEqual(plain(output.mapping), assets.mapping);
//     assert.deepEqual(day.counties[0].ageGroups, ages);
// });
// 
// test('table request size does not grow with simulation duration', () => {
//     const short = selectDay([day], 0, assets);
//     const long = selectDay(Array(212).fill(day), 211, assets);
//     assert.equal(JSON.stringify(short), JSON.stringify(long));
//     assert.equal(selectDay([], 0, {}), null);
//     assert.equal(selectDay([day], null, {}), null);
// });
// 
// function trigger(prop) {
//     context.window.dash_clientside.callback_context.triggered = [{prop_id: prop}];
// }
// const ids = [{type: 'county-age-toggle', fips: '01001'}, {type: 'county-age-toggle', fips: '01003'}];
// 
// const labels = ['0-4 years', '5-17 years', '18-49 years', '50-64 years', '65+ years'];
// const ageGroups = labels.map((_, index) => ({infected: (index + 1) * 40, deceased: index * 4,
//     infectedPercent: 6.76, deceasedPercent: 0.67}));
// function update(open, expanded, timestamps = [100, -1], history = [],
//                 clickState = {state: 'Texas', timestamp: expanded.length ? 100 : -1}, state = 'Texas') {
//     return updateRow(timestamps, {}, state, history, 0, 'count', 'seihrd-stochastic',
//         ids, open, ['Autauga', 'Baldwin'], expanded, labels, clickState);
// }
// 
// test('click opens immediately with loading content even without age data', () => {
//     trigger(JSON.stringify(ids[0]) + '.n_clicks');
//     const result = update([false, false], []);
//     assert.equal(result[0][0], true);
//     assert.equal(result[1][0].props.className, 'bi bi-chevron-down');
//     assert.equal(result[2][0], 'true');
//     assert.equal(result[3][0], 'Hide age breakdown for Autauga');
//     assert.equal(result[4][0].props.children, 'Loading age breakdown…');
//     assert.deepEqual(plain(result[5]), ['01001']);
// });
// 
// test('opening a second county closes the previous one', () => {
//     trigger(JSON.stringify(ids[1]) + '.n_clicks');
//     const result = update([true, false], ['01001'], [100, 200]);
//     assert.deepEqual(plain(result[0]), [false, true]);
//     assert.deepEqual(plain(result[2]), ['false', 'true']);
//     assert.deepEqual(plain(result[5]), ['01003']);
// });
// 
// test('clicking open county closes it; recreated buttons do not toggle it', () => {
//     trigger(JSON.stringify(ids[0]) + '.n_clicks');
//     const closed = update([true, false], ['01001'], [200, -1]);
//     assert.equal(closed[0][0], false);
//     assert.deepEqual(plain(closed[5]), []);
//     const recreated = update([true, false], ['01001'], [-1, -1]);
//     assert.equal(recreated[0][0], noUpdate);
//     assert.equal(recreated[5], noUpdate);
// });
// 
// test('state changes close the open county', () => {
//     trigger('selected-state-store.data');
//     const result = update([true, false], ['01001'], [100, -1], [],
//         {state: 'Texas', timestamp: 100}, 'Alabama');
//     assert.equal(result[0][0], false);
//     assert.deepEqual(plain(result[5]), []);
// });
// 
// test('a delayed table rerender restores selected expansion', () => {
//     trigger('spread-table.children');
//     const result = update([false, false], ['01001'], [-1, -1]);
//     assert.equal(result[0][0], true);
//     assert.equal(result[5], noUpdate);
// });
// 
// test('loaded age data renders five rows with formatted counts and percentages', () => {
//     const history = [{'01001': ageGroups}];
//     const count = ageContent(history, 0, '01001', 'count', 'seihrd-stochastic', labels);
//     const table = count.props.children[1];
//     assert.equal(table.props.children[1].props.children.length, 5);
//     const first = table.props.children[1].props.children[0].props.children;
//     assert.deepEqual(plain(first.map(cell => cell.props.children)), ['0-4 years', '40', '0']);
//     assert.equal(table.props.children[0].props.children.props.children[2].props.children, 'Deceased');
//     const percent = ageContent(history, 0, '01001', 'percent', 'seirs-stochastic', labels);
//     const percentageTable = percent.props.children[1];
//     assert.equal(percentageTable.props.children[0].props.children.props.children[2].props.children, 'Recovered');
//     const firstPercent = percentageTable.props.children[1].props.children[0].props.children;
//     assert.deepEqual(plain(firstPercent.map(cell => cell.props.children)), ['0-4 years', '6.8%', '0.7%']);
// });
// 
// test('pending history and explicit unavailable data are distinct', () => {
//     assert.match(ageContent([], 0, '01001', 'count', '', labels).props.children, /Loading/);
//     assert.match(ageContent([{'01001': null}], 0, '01001', 'count', '', labels).props.children, /unavailable/);
// });
// 
// test('new day age data updates open content without changing expansion', () => {
//     trigger('county-age-history.data');
//     const result = update([true, false], ['01001'], [100, -1], [{'01001': ageGroups}]);
//     assert.equal(result[0][0], noUpdate);
//     assert.equal(result[5], noUpdate);
//     assert.equal(result[4][0].props.children[1].type, 'Table');
// });
// 
// test('a click batched behind an age-data update still opens the county', () => {
//     context.window.dash_clientside.callback_context.triggered = [
//         {prop_id: 'county-age-history.data'},
//         {prop_id: JSON.stringify(ids[0]) + '.n_clicks'}
//     ];
//     const result = update([false, false], []);
//     assert.equal(result[0][0], true);
// });
// 
// // Real Dash callbacks may keep old timestamps in unchanged button props.
// test('consumed clicks are not replayed by subsequent table or age updates', () => {
//     const result = update([true, false], ['01001'], [100, -1]);
//     assert.equal(result[0][0], noUpdate);
//     assert.equal(result[5], noUpdate);
//     assert.equal(result[6], noUpdate);
// });
// 
// test('batched clicks use the latest timestamp even with no callback context', () => {
//     const saved = context.window.dash_clientside.callback_context;
//     delete context.window.dash_clientside.callback_context;
//     try {
//         const result = update([false, false], [], [100, 200]);
//         assert.equal(result[0][1], true);
//         assert.deepEqual(plain(result[5]), ['01003']);
//         assert.deepEqual(plain(result[6]), {state: 'Texas', timestamp: 200});
//     } finally {
//         context.window.dash_clientside.callback_context = saved;
//     }
// });
// 
// test('the first click also works before the click-state store is initialized', () => {
//     const result = update([false, false], [], [100, -1], [], {state: null, timestamp: -1});
//     assert.equal(result[0][0], true);
//     assert.deepEqual(plain(result[5]), ['01001']);
// });
