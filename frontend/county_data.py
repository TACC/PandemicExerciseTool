"""Convert PES compartment output to county and age-specific table metrics."""

from constants import AGE_GROUPS


def compartment_metrics(summary):
    infectious = sum(float(summary.get(key, 0) or 0) for key in ('A', 'I', 'T', 'IA', 'IP', 'IS'))
    outcome = float(summary.get('D', summary.get('R', 0)) or 0)
    population = sum(float(value or 0) for value in summary.values())
    return {
        'infected': infectious,
        # This legacy key holds recovered counts for models without deaths.
        'deceased': outcome,
        'infectedPercent': infectious / population * 100 if population else 0,
        'deceasedPercent': outcome / population * 100 if population else 0,
    }


def county_metrics(county):
    result = {
        'fips': str(county.get('fips_id', '')).zfill(5),
        **compartment_metrics(county.get('compartment_summary', {})),
        'ageGroups': None,
    }
    subgroups = county.get('compartment_subgroups')
    if not subgroups:
        return result

    summaries = [{} for _ in AGE_GROUPS]
    for compartment, risks in subgroups.items():
        for vaccinations in risks.values():
            for ages in vaccinations.values():
                if len(ages) != len(AGE_GROUPS):
                    # Incomplete output is unavailable, rather than a zero count.
                    return result
                for index, value in enumerate(ages):
                    summaries[index][compartment] = (
                        summaries[index].get(compartment, 0) + float(value or 0)
                    )
    result['ageGroups'] = [compartment_metrics(summary) for summary in summaries]
    return result
