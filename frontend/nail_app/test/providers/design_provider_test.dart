import 'package:flutter_test/flutter_test.dart';
import 'package:nail_app/models/design_plan.dart';
import 'package:nail_app/providers/design_provider.dart';
import 'package:nail_app/services/design_service.dart';

class FakeDesignService extends DesignService {
  DesignPlanListResponse? listResponse;
  DesignPlan? designToReturn;
  List<DesignPlan>? versionsToReturn;
  Exception? error;

  @override
  Future<DesignPlanListResponse> getDesigns({
    int skip = 0,
    int limit = 20,
    int? customerId,
    String? search,
    int? isArchived,
  }) async {
    if (error != null) throw error!;
    return listResponse!;
  }

  @override
  Future<DesignPlan> generateDesign({
    required String prompt,
    List<String>? referenceImages,
    String designTarget = '10nails',
    List<String>? styleKeywords,
    int? customerId,
    String? title,
    String? notes,
  }) async {
    if (error != null) throw error!;
    return designToReturn!;
  }

  @override
  Future<DesignPlan> refineDesign(int designId, String instruction) async {
    if (error != null) throw error!;
    return designToReturn!;
  }

  @override
  Future<DesignPlan> getDesign(int id) async {
    if (error != null) throw error!;
    return designToReturn!;
  }

  @override
  Future<List<DesignPlan>> getDesignVersions(int id) async {
    return versionsToReturn ?? [];
  }

  @override
  Future<void> archiveDesign(int id) async {
    if (error != null) throw error!;
  }

  @override
  Future<void> deleteDesign(int id) async {
    if (error != null) throw error!;
  }
}

void main() {
  late FakeDesignService fakeService;
  late DesignProvider provider;

  final now = DateTime.now();

  DesignPlan makeDesign(int id, {int version = 1, int? parentId}) =>
      DesignPlan(
        id: id,
        userId: 1,
        aiPrompt: '粉色渐变',
        generatedImagePath: '/designs/$id.png',
        version: version,
        parentDesignId: parentId,
        isArchived: 0,
        createdAt: now,
        updatedAt: now,
      );

  setUp(() {
    fakeService = FakeDesignService();
    provider = DesignProvider(service: fakeService);
  });

  group('DesignProvider', () {
    test('initial state', () {
      expect(provider.designs, isEmpty);
      expect(provider.isLoading, false);
      expect(provider.isGenerating, false);
      expect(provider.error, isNull);
    });

    test('loadDesigns success', () async {
      fakeService.listResponse = DesignPlanListResponse(
        total: 2,
        designs: [makeDesign(1), makeDesign(2)],
      );

      await provider.loadDesigns();

      expect(provider.designs.length, 2);
      expect(provider.total, 2);
      expect(provider.isLoading, false);
    });

    test('generateDesign success adds to list', () async {
      fakeService.designToReturn = makeDesign(1);

      final result = await provider.generateDesign(prompt: '粉色渐变');

      expect(result, isNotNull);
      expect(provider.designs.length, 1);
      expect(provider.selectedDesign, isNotNull);
      expect(provider.isGenerating, false);
    });

    test('generateDesign error sets error', () async {
      fakeService.error = Exception('500 Internal Server Error');

      final result = await provider.generateDesign(prompt: 'test');

      expect(result, isNull);
      expect(provider.error, contains('AI'));
      expect(provider.isGenerating, false);
    });

    test('deleteDesign removes from list', () async {
      fakeService.listResponse = DesignPlanListResponse(
        total: 1,
        designs: [makeDesign(1)],
      );
      await provider.loadDesigns();

      fakeService.error = null;
      final result = await provider.deleteDesign(1);

      expect(result, true);
      expect(provider.designs, isEmpty);
    });

    test('refineDesign adds new version', () async {
      fakeService.listResponse = DesignPlanListResponse(
        total: 1,
        designs: [makeDesign(1)],
      );
      await provider.loadDesigns();

      final refined = makeDesign(2, version: 2, parentId: 1);
      fakeService.designToReturn = refined;
      fakeService.error = null;
      final result = await provider.refineDesign(1, '增加亮片');

      expect(result, isNotNull);
      expect(result!.version, 2);
      expect(result.parentDesignId, 1);
      expect(provider.designs.length, 2);
    });
  });
}
