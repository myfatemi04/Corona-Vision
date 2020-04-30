interface TotalsSequence {
    entry_date: string[];
    total: number[],
    recovered: number[],
    deaths: number[]
}

interface Datapoint {
    entry_date: string;
    update_time: Date;

    country: string,
    province: string,
    county: string,

    total: number;
    recovered: number;
    deaths: number;
    serious: number;
    tests: number;
}