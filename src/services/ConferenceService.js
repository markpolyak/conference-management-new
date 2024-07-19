import $api from "../api/api";
import { API_ENDPOINTS } from "../api/apiEndpoints";

export default class ConferenceService {
  
  static async fetchConferences(filter='') {
    const queryParams = filter ? {
      params: {
        filter: filter
      }
    }
      :  {
        params: {}
      };

    return $api.get(API_ENDPOINTS.CONFERENCES, queryParams).then((response) => response.data);
  }

  static async fetchConferenceById(id) {
    // return $api.get(`API_ENDPOINTS.CONFERENCE_ID/${id}`).then((response) => response.data);
    const url = (Number(id) % 2 === 0) ? "/conference_id1.json" : "/conference_id2.json"
    return $api.get(url).then((response) => response.data);
  }

  // static async setConferences(conference) {
  //   return $api
  //     .put(API_ENDPOINTS.COMMISSIONS, commission)
  //     .then((response) => response.data);
  // }

  // static async addCommission(settings) {
  //   return $api
  //     .post(API_ENDPOINTS.COMMISSIONS, settings)
  //     .then((response) => response.data);
  // }
}