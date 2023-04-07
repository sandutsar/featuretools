import pandas as pd
from woodwork.column_schema import ColumnSchema
from woodwork.logical_types import Datetime, Double

from featuretools.primitives.base.transform_primitive_base import TransformPrimitive
from featuretools.primitives.standard.transform.time_series.utils import (
    _apply_gap_for_expanding_primitives,
)
from featuretools.utils import calculate_trend


class ExpandingTrend(TransformPrimitive):
    """Computes the expanding trend for events over a given window.

    Description:
        Given a list of datetimes, returns the expanding trend starting
        at the row `gap` rows away from the current row. An expanding
        primitive calculates the value of a primitive for a given time
        with all the data available up to the corresponding point in time.

        Input datetimes should be monotonic.

    Args:
        gap (int, optional): Specifies a gap backwards from each instance before the
            usable data begins. Corresponds to number of rows. Defaults to 1.
        min_periods (int, optional): Minimum number of observations required for performing calculations
            over the window. Defaults to 1.


    Examples:
        >>> import pandas as pd
        >>> expanding_trend = ExpandingTrend()
        >>> times = pd.date_range(start='2019-01-01', freq='1D', periods=5)
        >>> ans = expanding_trend(times, [5, 4, 3, 2, 1]).tolist()
        >>> [round(x, 2) for x in ans]
        [nan, nan, nan, -1.0, -1.0]

        We can also control the gap before the expanding calculation.

        >>> import pandas as pd
        >>> expanding_trend = ExpandingTrend(gap=0)
        >>> times = pd.date_range(start='2019-01-01', freq='1D', periods=5)
        >>> ans = expanding_trend(times, [5, 4, 3, 2, 1]).tolist()
        >>> [round(x, 2) for x in ans]
        [nan, nan, -1.0, -1.0, -1.0]

        We can also control the minimum number of periods required for the rolling calculation.

        >>> import pandas as pd
        >>> expanding_trend = ExpandingTrend(min_periods=3)
        >>> times = pd.date_range(start='2019-01-01', freq='1min', periods=5)
        >>> ans = expanding_trend(times, [50, 4, 13, 22, 10]).tolist()
        >>> [round(x, 2) for x in ans]
        [nan, nan, nan, -18.5, -7.5]
    """

    name = "expanding_trend"
    input_types = [
        ColumnSchema(logical_type=Datetime, semantic_tags={"time_index"}),
        ColumnSchema(semantic_tags={"numeric"}),
    ]
    return_type = ColumnSchema(logical_type=Double, semantic_tags={"numeric"})
    uses_full_dataframe = True

    def __init__(self, gap=1, min_periods=1):
        self.gap = gap
        self.min_periods = min_periods

    def get_function(self):
        def expanding_trend(datetime, numeric):
            x = pd.Series(numeric.values, index=datetime)
            x = _apply_gap_for_expanding_primitives(x, self.gap)
            return (
                x.expanding(min_periods=self.min_periods)
                .aggregate(calculate_trend)
                .values
            )

        return expanding_trend
