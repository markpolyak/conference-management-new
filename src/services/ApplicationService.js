import $api from "../api/api";
import { API_ENDPOINTS } from "../api/apiEndpoints";

export default class ApplicationService {
  static async fetchApplications(id, email="123@mail.ru") {
    const queryParams = email ? {
      params: {
        email: email
      }
    }
      :  {
        params: {}
      };
    // return $api.get(`${API_ENDPOINTS.APPLICATIONS}/${id}`).then((response) => response.data);
    return $api.get(`${API_ENDPOINTS.APPLICATIONS}`, queryParams).then((response) => response.data);
  }

  static async addApplication(application) {
    return $api.post(API_ENDPOINTS.APPLICATION, application).then((response) => response.data);
  }

  static async editApplication(conferenceId, application) {
    return $api.patch(`.conferences/${conferenceId}/applications/${application.id}`, application).then((response) => response.data);
  }

  static async deleteApplication(id) {
    return $api.delete(API_ENDPOINTS.APPLICATION, id).then((response) => response.data);
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