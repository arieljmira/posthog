from freezegun import freeze_time

from posthog.hogql_queries.error_tracking_query_runner import ErrorTrackingQueryRunner
from posthog.schema import (
    ErrorTrackingQuery,
    DateRange,
)
from posthog.test.base import (
    APIBaseTest,
    ClickhouseTestMixin,
    snapshot_clickhouse_queries,
    _create_person,
    _create_event,
    flush_persons_and_events,
)


class TestErrorTrackingQueryRunner(ClickhouseTestMixin, APIBaseTest):
    distinct_id_one = "user_1"
    distinct_id_two = "user_2"

    def setUp(self):
        super().setUp()

        with freeze_time("2020-01-10 12:11:00"):
            _create_person(
                team=self.team,
                distinct_ids=[self.distinct_id_one],
                is_identified=True,
            )
            _create_person(
                team=self.team,
                properties={
                    "email": "email@posthog.com",
                    "name": "Test User",
                },
                distinct_ids=[self.distinct_id_two],
                is_identified=True,
            )

            _create_event(
                distinct_id=self.distinct_id_one,
                event="$exception",
                team=self.team,
                properties={
                    "$exception_fingerprint": "SyntaxError",
                },
            )
            _create_event(
                distinct_id=self.distinct_id_one,
                event="$exception",
                team=self.team,
                properties={
                    "$exception_fingerprint": "TypeError",
                },
            )
            _create_event(
                distinct_id=self.distinct_id_two,
                event="$exception",
                team=self.team,
                properties={
                    "$exception_fingerprint": "SyntaxError",
                },
            )
            _create_event(
                distinct_id=self.distinct_id_two,
                event="$exception",
                team=self.team,
                properties={
                    "$exception_fingerprint": "custom_fingerprint",
                },
            )

        flush_persons_and_events()

    def _calculate(self, runner: ErrorTrackingQueryRunner):
        return runner.calculate().model_dump()

    # @snapshot_clickhouse_queries
    # def test_column_names(self):
    #     runner = ErrorTrackingQueryRunner(
    #         team=self.team,
    #         query=ErrorTrackingQuery(
    #             kind="ErrorTrackingQuery",
    #             select=[],
    #             fingerprint=None,
    #             dateRange=DateRange(),
    #             filterTestAccounts=True,
    #         ),
    #     )

    #     columns = self._calculate(runner)["columns"]
    #     self.assertEqual(columns, ["fingerprint", "context.columns.error", "occurrences"])

    @snapshot_clickhouse_queries
    def test_fingerprints(self):
        runner = ErrorTrackingQueryRunner(
            team=self.team,
            query=ErrorTrackingQuery(
                kind="ErrorTrackingQuery",
                select=[],
                fingerprint="SyntaxError",
                dateRange=DateRange(),
            ),
        )

        results = self._calculate(runner)["results"]
        # returns a single group with multiple errors
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["fingerprint"], "SyntaxError")
        self.assertEqual(results[0]["occurrences"], 3)

    # def test_only_returns_exception_events(self):
    #     with freeze_time("2020-01-10 12:11:00"):
    #         _create_event(
    #             distinct_id=self.distinct_id_one,
    #             event="$pageview",
    #             team=self.team,
    #             properties={
    #                 "$exception_fingerprint": "SyntaxError",
    #             },
    #         )
    #     flush_persons_and_events()

    #     runner = ErrorTrackingQueryRunner(
    #         team=self.team,
    #         query=ErrorTrackingQuery(
    #             kind="ErrorTrackingQuery",
    #             select=["count() as occurrences"],
    #             dateRange=DateRange(),
    #         ),
    #     )

    #     results = self._calculate(runner)["results"]
    #     self.assertEqual(len(results), 3)

    # @snapshot_clickhouse_queries
    # def test_hogql_filters(self):
    #     runner = ErrorTrackingQueryRunner(
    #         team=self.team,
    #         query=ErrorTrackingQuery(
    #             kind="ErrorTrackingQuery",
    #             select=["count() as occurrences"],
    #             dateRange=DateRange(),
    #             filterGroup=PropertyGroupFilter(
    #                 type=FilterLogicalOperator.AND_,
    #                 values=[
    #                     PropertyGroupFilterValue(
    #                         type=FilterLogicalOperator.OR_,
    #                         values=[
    #                             PersonPropertyFilter(
    #                                 key="email", value="email@posthog.com", operator=PropertyOperator.EXACT
    #                             ),
    #                         ],
    #                     )
    #                 ],
    #             ),
    #         ),
    #     )

    #     results = self._calculate(runner)["results"]
    #     # two errors exist for person with distinct_id_two
    #     self.assertEqual(len(results), 2)

    # def test_merges_and_defaults_groups(self):
    #     ErrorTrackingGroup.objects.create(
    #         team=self.team, fingerprint="SyntaxError", merged_fingerprints=["custom_fingerprint"], assignee=self.user
    #     )

    #     runner = ErrorTrackingQueryRunner(
    #         team=self.team,
    #         query=ErrorTrackingQuery(
    #             kind="ErrorTrackingQuery",
    #             select=["count() as occurrences"],
    #             fingerprint=None,
    #             dateRange=DateRange(),
    #         ),
    #     )

    #     results = self._calculate(runner)["results"]
    #     self.assertEqual(
    #         results,
    #         [
    #             {
    #                 "fingerprint": "SyntaxError",
    #                 "merged_fingerprints": ["custom_fingerprint"],
    #                 "status": "active",
    #                 "assignee": self.user.id,
    #                 # count is (2 x SyntaxError) + (1 x custom_fingerprint)
    #                 "occurrences": 3,
    #             },
    #             {
    #                 "fingerprint": "TypeError",
    #                 "assignee": None,
    #                 "merged_fingerprints": [],
    #                 "status": "active",
    #                 "occurrences": 1,
    #             },
    #         ],
    #     )
