import requests
import upload
import time
from data_sources import minWait

lastDatapointsUpdate = 0

### Don't use this. ###

def import_data():
    global lastDatapointsUpdate

    queryURL = "https://wabi-south-central-us-api.analysis.windows.net/public/reports/querydata?synchronous=true"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,es;q=0.6",
        "activityid": "73596499-c161-3cb3-3478-db0fbfe3e010",
        "content-type": "application/json;charset=UTF-8",
        "requestid": "82cd9696-4834-f937-953c-36861741320b",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "x-powerbi-resourcekey": "00bb2ed2-5593-44c0-9576-7b1d07d2a07e"
    }

    body = {
        "version":"1.0.0",
        "queries":[
            {"Query":
                {"Commands":
                    [
                        {"SemanticQueryDataShapeCommand":
                            {"Query":
                                {"Version":2,
                                    "From":[
                                        {"Name":"v","Entity":"vw_departamento"},
                                        {"Name":"m","Entity":"MEDIDAS"}
                                    ],
                                    "Select":[
                                        {"Column":
                                            {"Expression":
                                                {"SourceRef":
                                                    {"Source":"v"}
                                                },
                                            "Property":"Departamento"},
                                            "Name":"vw_departamento.Departamento"
                                        },
                                        {"Measure":
                                            {"Expression":
                                                {"SourceRef":
                                                    {"Source":"m"}
                                                },
                                            "Property":"N_POSITIVOS_DEP"},
                                            "Name":"MEDIDAS.N_POSITIVOS_DEP"},
                                        {"Measure":
                                            {"Expression":
                                                {"SourceRef":
                                                    {"Source":"m"}
                                                },
                                            "Property":"N_Confirmados"},
                                            "Name":"MEDIDAS.N_Confirmados"},
                                        {"Measure":
                                            {"Expression":
                                                {"SourceRef":
                                                    {"Source":"m"}
                                                },
                                            "Property":"N_Resumen_conf+posit"},
                                            "Name":"MEDIDAS.N_Resumen_conf+posit"},
                                        {"Measure":
                                            {"Expression":
                                                {"SourceRef":
                                                    {"Source":"m"}
                                                },
                                                "Property":"N_Fallecidos_Cero"},
                                                "Name":"MEDIDAS.N_Fallecidos_Cero"},
                                        {"Measure":
                                            {"Expression":
                                                {"SourceRef":
                                                    {"Source":"m"}
                                                },
                                                "Property":"M_%_Letalidad_Resumen"},
                                                "Name":"MEDIDAS.M_%_Letalidad_Resumen"},
                                        {"Column":
                                            {"Expression":
                                                {"SourceRef":
                                                    {"Source":"v"}
                                                },
                                                "Property":"Pais"},
                                                "Name":"vw_departamento.Pais"}
                                    ],
                                    "OrderBy":[
                                        {"Direction":2,
                                            "Expression":{
                                                "Measure":{
                                                    "Expression":{
                                                        "SourceRef":{"Source":"m"}
                                                    },
                                                    "Property":"N_POSITIVOS_DEP"}
                                            }
                                        }
                                    ]
                                },
                                "Binding":{
                                    "Primary":{
                                        "Groupings":[
                                            {"Projections":[6],"Subtotal":1},
                                            {"Projections":[0,1,2,3,4,5],"Subtotal":1}
                                        ],
                                    "Expansion":{
                                        "From":[
                                            {"Name":"v","Entity":"vw_departamento"}
                                        ],
                                        "Levels":[
                                            {"Expressions":[
                                                {"Column":{
                                                    "Expression":{
                                                        "SourceRef":{"Source":"v"}
                                                    },
                                                    "Property":"Pais"}
                                                }
                                            ],
                                            "Default":0}
                                        ],
                                        "Instances":
                                            {"Children":[
                                                {"Values":[
                                                    {"Literal":{"Value":"'Perú'"}}
                                                ]},
                                                {"Values":[
                                                    {"Literal":{"Value":"'PERÜ'"}}
                                                ]},
                                                {"Values":[
                                                    {"Literal":{"Value":"'PERÚ'"}}
                                                ]}
                                            ]}
                                        }
                                    },
                                    "DataReduction":{
                                        "DataVolume":3,
                                        "Primary":{
                                            "Window":{"Count":500}
                                        }
                                    },
                                    "Version":1
                                }
                            }
                        }
                    ]
                },
                "CacheKey":
                    "{\"Commands\":[{\"SemanticQueryDataShapeCommand\":{\"Query\":{\"Version\":2,\"From\":[{\"Name\":\"v\",\"Entity\":\"vw_departamento\"},{\"Name\":\"m\",\"Entity\":\"MEDIDAS\"}],\"Select\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"v\"}},\"Property\":\"Departamento\"},\"Name\":\"vw_departamento.Departamento\"},{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"m\"}},\"Property\":\"N_POSITIVOS_DEP\"},\"Name\":\"MEDIDAS.N_POSITIVOS_DEP\"},{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"m\"}},\"Property\":\"N_Confirmados\"},\"Name\":\"MEDIDAS.N_Confirmados\"},{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"m\"}},\"Property\":\"N_Resumen_conf+posit\"},\"Name\":\"MEDIDAS.N_Resumen_conf+posit\"},{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"m\"}},\"Property\":\"N_Fallecidos_Cero\"},\"Name\":\"MEDIDAS.N_Fallecidos_Cero\"},{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"m\"}},\"Property\":\"M_%_Letalidad_Resumen\"},\"Name\":\"MEDIDAS.M_%_Letalidad_Resumen\"},{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"v\"}},\"Property\":\"Pais\"},\"Name\":\"vw_departamento.Pais\"}],\"OrderBy\":[{\"Direction\":2,\"Expression\":{\"Measure\":{\"Expression\":{\"SourceRef\":{\"Source\":\"m\"}},\"Property\":\"N_POSITIVOS_DEP\"}}}]},\"Binding\":{\"Primary\":{\"Groupings\":[{\"Projections\":[6],\"Subtotal\":1},{\"Projections\":[0,1,2,3,4,5],\"Subtotal\":1}],\"Expansion\":{\"From\":[{\"Name\":\"v\",\"Entity\":\"vw_departamento\"}],\"Levels\":[{\"Expressions\":[{\"Column\":{\"Expression\":{\"SourceRef\":{\"Source\":\"v\"}},\"Property\":\"Pais\"}}],\"Default\":0}],\"Instances\":{\"Children\":[{\"Values\":[{\"Literal\":{\"Value\":\"'Perú'\"}}]},{\"Values\":[{\"Literal\":{\"Value\":\"'PERÜ'\"}}]},{\"Values\":[{\"Literal\":{\"Value\":\"'PERÚ'\"}}]}]}}},\"DataReduction\":{\"DataVolume\":3,\"Primary\":{\"Window\":{\"Count\":500}}},\"Version\":1}}}]}",
                    "QueryId":"",
                    "ApplicationContext":{
                        "DatasetId":"5295e43e-3620-4a14-b332-6c5293efe177",
                        "Sources":[
                            {"ReportId":"fcb4b886-8ba4-44e1-92c6-08b525e9fb48"}
                        ]
                    }
            }
        ],
        "cancelQueries":[],
        "modelId":2930567
    }

    response = requests.post(queryURL, json=body, headers=headers).json()
    
    data = response['results'][0]['result']['data']['dsr']['DS'][0]['PH'][0]['DM0'][0]['C']

    datapoint = {
        'country': "Peru",
        'total': data[2],
        'deaths': data[3]
    }

    print(datapoint)

    # if upload.upload(result):
    #     lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()