from dataclasses import dataclass

import requests


@dataclass
class Client:
    url: str
    headers: dict

    def run_query(self, query: str, variables: dict, extract=False):
        request = requests.post(
            self.url,
            headers=self.headers,
            json={"query": query, "variables": variables},
        )
        assert request.ok, f"Failed with code {request.status_code}"
        return request.json()

    create_pair = lambda self, text, keywords: self.run_query(
        """
            mutation createPair($text: String!, $keywords: text_keyword_arr_rel_insert_input) {
                  insert_text(objects: [
                    {
                      text_value: $text, 
                      text_keywords: $keywords
                    }
                  ]) 
                  {
                    returning {
                      text_value
                      text_keywords {
                        keyword {
                          keyword_value
                        }
                      }
                    }
                  }
                }

        """,
        {"text": text, "keywords": keywords},
    )

    get_keywords = lambda self: self.run_query(
        """
        query getKeywords{
            keyword {
                keyword_value
            }
        }
        """, {}
    )

    get_pairs = lambda self: self.run_query(
        """
        query getPairs {
          text {
            text_value
            text_keywords {
              keyword {
                keyword_value
              }
            }
          }
        }
        """, {}
    )

    get_pairs_by_keywords = lambda self, keywords: self.run_query(
        """
        query getPairsByKeywords($list:[String!]){
          text_keyword(where: {keyword: {keyword_value: {_in: $list }}}) {
            text {
              text_value
              text_keywords {
                keyword {
                  keyword_value
                }
              }
            }
          }
        }
        """, {'list': keywords}
    )
