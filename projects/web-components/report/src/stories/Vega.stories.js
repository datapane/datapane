import Vega from "../components/blocks/Vega.vue";
import { makeTemplate } from "./utils";

export default {
    title: "Vega",
    component: Vega,
};

export const Primary = makeTemplate(Vega);

Primary.args = {
    responsive: true,
    plotJson: {
        config: { view: { continuousWidth: 400, continuousHeight: 300 } },
        data: { name: "data-1dade804818bb4a87ac30f362092e342" },
        mark: "line",
        encoding: {
            x: { field: "x", type: "quantitative" },
            y: { field: "f(x)", type: "quantitative" },
        },
        $schema: "https://vega.github.io/schema/vega-lite/v4.17.0.json",
        datasets: {
            "data-1dade804818bb4a87ac30f362092e342": [
                { x: 0, "f(x)": 0 },
                { x: 1, "f(x)": 0.19866933079506122 },
                { x: 2, "f(x)": 0.3894183423086505 },
                { x: 3, "f(x)": 0.5646424733950354 },
                { x: 4, "f(x)": 0.7173560908995228 },
                { x: 5, "f(x)": 0.8414709848078965 },
                { x: 6, "f(x)": 0.9320390859672263 },
                { x: 7, "f(x)": 0.9854497299884601 },
                { x: 8, "f(x)": 0.9995736030415051 },
                { x: 9, "f(x)": 0.9738476308781951 },
                { x: 10, "f(x)": 0.9092974268256817 },
                { x: 11, "f(x)": 0.8084964038195901 },
                { x: 12, "f(x)": 0.675463180551151 },
                { x: 13, "f(x)": 0.5155013718214642 },
                { x: 14, "f(x)": 0.33498815015590505 },
                { x: 15, "f(x)": 0.1411200080598672 },
                { x: 16, "f(x)": -0.058374143427580086 },
                { x: 17, "f(x)": -0.2555411020268312 },
                { x: 18, "f(x)": -0.44252044329485246 },
                { x: 19, "f(x)": -0.6118578909427189 },
                { x: 20, "f(x)": -0.7568024953079282 },
                { x: 21, "f(x)": -0.8715757724135881 },
                { x: 22, "f(x)": -0.9516020738895161 },
                { x: 23, "f(x)": -0.9936910036334644 },
                { x: 24, "f(x)": -0.9961646088358407 },
                { x: 25, "f(x)": -0.9589242746631385 },
                { x: 26, "f(x)": -0.8834546557201531 },
                { x: 27, "f(x)": -0.7727644875559871 },
                { x: 28, "f(x)": -0.6312666378723216 },
                { x: 29, "f(x)": -0.46460217941375737 },
                { x: 30, "f(x)": -0.27941549819892586 },
                { x: 31, "f(x)": -0.08308940281749641 },
                { x: 32, "f(x)": 0.11654920485049364 },
                { x: 33, "f(x)": 0.31154136351337786 },
                { x: 34, "f(x)": 0.4941133511386082 },
                { x: 35, "f(x)": 0.6569865987187891 },
                { x: 36, "f(x)": 0.7936678638491531 },
                { x: 37, "f(x)": 0.8987080958116269 },
                { x: 38, "f(x)": 0.9679196720314863 },
                { x: 39, "f(x)": 0.998543345374605 },
                { x: 40, "f(x)": 0.9893582466233818 },
                { x: 41, "f(x)": 0.9407305566797731 },
                { x: 42, "f(x)": 0.8545989080882805 },
                { x: 43, "f(x)": 0.7343970978741134 },
                { x: 44, "f(x)": 0.5849171928917617 },
                { x: 45, "f(x)": 0.4121184852417566 },
                { x: 46, "f(x)": 0.22288991410024764 },
                { x: 47, "f(x)": 0.024775425453357765 },
                { x: 48, "f(x)": -0.17432678122297965 },
                { x: 49, "f(x)": -0.3664791292519284 },
                { x: 50, "f(x)": -0.5440211108893699 },
                { x: 51, "f(x)": -0.6998746875935424 },
                { x: 52, "f(x)": -0.8278264690856536 },
                { x: 53, "f(x)": -0.9227754216128066 },
                { x: 54, "f(x)": -0.9809362300664916 },
                { x: 55, "f(x)": -0.9999902065507035 },
                { x: 56, "f(x)": -0.9791777291513174 },
                { x: 57, "f(x)": -0.9193285256646757 },
                { x: 58, "f(x)": -0.8228285949687089 },
                { x: 59, "f(x)": -0.6935250847771224 },
                { x: 60, "f(x)": -0.5365729180004349 },
                { x: 61, "f(x)": -0.3582292822368287 },
                { x: 62, "f(x)": -0.1656041754483094 },
                { x: 63, "f(x)": 0.03362304722113669 },
                { x: 64, "f(x)": 0.23150982510153895 },
                { x: 65, "f(x)": 0.4201670368266409 },
                { x: 66, "f(x)": 0.592073514707223 },
                { x: 67, "f(x)": 0.7403758899524486 },
                { x: 68, "f(x)": 0.8591618148564959 },
                { x: 69, "f(x)": 0.9436956694441048 },
                { x: 70, "f(x)": 0.9906073556948704 },
                { x: 71, "f(x)": 0.9980266527163617 },
                { x: 72, "f(x)": 0.9656577765492775 },
                { x: 73, "f(x)": 0.8947911721405042 },
                { x: 74, "f(x)": 0.7882520673753163 },
                { x: 75, "f(x)": 0.6502878401571169 },
                { x: 76, "f(x)": 0.4863986888537997 },
                { x: 77, "f(x)": 0.30311835674570226 },
                { x: 78, "f(x)": 0.10775365229944406 },
                { x: 79, "f(x)": -0.09190685022768165 },
                { x: 80, "f(x)": -0.2879033166650653 },
                { x: 81, "f(x)": -0.47242198639846616 },
                { x: 82, "f(x)": -0.6381066823479474 },
                { x: 83, "f(x)": -0.7783520785342986 },
                { x: 84, "f(x)": -0.8875670335815046 },
                { x: 85, "f(x)": -0.9613974918795568 },
                { x: 86, "f(x)": -0.9969000660415961 },
                { x: 87, "f(x)": -0.9926593804706332 },
                { x: 88, "f(x)": -0.948844497918124 },
                { x: 89, "f(x)": -0.8672021794855813 },
                { x: 90, "f(x)": -0.750987246771676 },
                { x: 91, "f(x)": -0.6048328224062841 },
                { x: 92, "f(x)": -0.4345656220718967 },
                { x: 93, "f(x)": -0.2469736617366209 },
                { x: 94, "f(x)": -0.04953564087836742 },
                { x: 95, "f(x)": 0.14987720966295234 },
                { x: 96, "f(x)": 0.3433149288198954 },
                { x: 97, "f(x)": 0.5230657651576964 },
                { x: 98, "f(x)": 0.6819636200681355 },
                { x: 99, "f(x)": 0.8136737375071054 },
            ],
        },
    },
};
