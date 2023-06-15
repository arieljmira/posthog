import { BatchExport, BatchExportData, BatchExportsResponse } from './api'

export const createExportServiceHandlers = (): { exports: { [id: number]: BatchExport }; handlers: any } => {
    const exports: { [id: number]: BatchExport } = {
        1: {
            id: 'asdf',
            team_id: 1,
            name: 'S3',
            destination: {
                type: 'S3',
                config: {
                    bucket_name: 'my-bucket',
                    region: 'us-east-1',
                    prefix: 'my-prefix',
                    aws_access_key_id: 'my-access-key-id',
                    aws_secret_access_key: '',
                },
            },
            interval: 'hour',
            status: 'RUNNING',
            paused: false,
            created_at: '2021-09-01T00:00:00.000000Z',
            last_updated_at: '2021-09-01T00:00:00.000000Z',
        },
    }

    const handlers = {
        get: {
            '/api/projects/:team_id/batch_exports/': (_req: any, res: any, ctx: any) => {
                return res(
                    ctx.delay(1000),
                    ctx.json({
                        results: Object.values(exports),
                    } as BatchExportsResponse)
                )
            },
            '/api/projects/:team_id/batch_exports/:export_id': (req: any, res: any, ctx: any) => {
                const id = req.params.export_id as string
                return res(ctx.delay(1000), ctx.json(exports[id]))
            },
            '/api/projects/:team_id/batch_exports/:export_id/runs': (req: any, res: any, ctx: any) => {
                const id = req.params.export_id as string
                return res(
                    ctx.delay(1000),
                    ctx.json({
                        results: [
                            {
                                export_id: id,
                                run_id: 1,
                                status: 'RUNNING',
                                created_at: '2021-09-01T00:00:00.000000Z',
                                last_updated_at: '2021-09-01T00:00:00.000000Z',
                            },
                        ],
                    })
                )
            },
        },
        post: {
            '/api/projects/:team_id/batch_exports/': (req: any, res: any, ctx: any) => {
                const body = req.body as BatchExportData
                const id = (Object.keys(exports).length + 1).toString()
                exports[id] = {
                    ...body,
                    id: id,
                    team_id: 1,
                    status: 'RUNNING',
                    paused: false,
                    created_at: new Date().toISOString(),
                    last_updated_at: new Date().toISOString(),
                }
                return res(ctx.delay(1000), ctx.json(exports[id]))
            },
        },
    }

    return { handlers, exports }
}
