// Browser-side projection: full history and polygons stay in the browser.
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    incrementalMap: {
        selectFrame: function (events, timeline, view, selectedCounty, metadata, state, assets) {
            if (!metadata || metadata.state !== state) {
                return null;
            }
            const day = events && timeline != null ? events[timeline] : null;
            const byFips = {};
            const prefix = metadata.fips[0].slice(0, 2);
            for (const county of (day || {}).counties || []) {
                let fips = String(county.fips || '').trim();
                if (!fips) continue;
                fips = fips.length === 3 ? prefix + fips : fips.padStart(5, '0');
                byFips[fips] = county;
            }
            const values = [];
            const customdata = [];
            metadata.fips.forEach(function (fips, index) {
                const county = byFips[fips] || {};
                const infected = county.infected || 0;
                const percent = county.infectedPercent || 0;
                values.push(view === 'percent' ? percent : infected);
                customdata.push([metadata.names[index], infected, percent, county.deceased || 0]);
            });
            const highlight = {lon: [], lat: []};
            if (selectedCounty && metadata.fips.includes(selectedCounty)) {
                const feature = (((assets || {}).geojson || {}).features || []).find(
                    feature => feature.properties.GEOID === selectedCounty
                );
                if (feature) {
                    const geometry = feature.geometry;
                    const polygons = geometry.type === 'MultiPolygon' ? geometry.coordinates : [geometry.coordinates];
                    for (const polygon of polygons) {
                        for (const ring of polygon) {
                            if (highlight.lon.length) {
                                highlight.lon.push(null);
                                highlight.lat.push(null);
                            }
                            for (const point of ring) {
                                highlight.lon.push(point[0]);
                                highlight.lat.push(point[1]);
                            }
                        }
                    }
                }
            }
            return {state: state, day: day ? day.day : null, view: view, values: values,
                customdata: customdata, highlight: highlight};
        }
    }
});
