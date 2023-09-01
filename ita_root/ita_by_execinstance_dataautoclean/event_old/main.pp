import json
import sys
import time
from master.T_EVRL_EVENT                     import T_EVRL_EVENT
from master.T_EVRL_EVENT_COLLECTION_PROGRESS import T_EVRL_EVENT_COLLECTION_PROGRESS
from master.T_EVRL_FILTER                    import T_EVRL_FILTER
from master.T_EVRL_LABEL_KEY_CONCLUSION      import T_EVRL_LABEL_KEY_CONCLUSION
from master.T_EVRL_LABEL_KEY_INPUT           import T_EVRL_LABEL_KEY_INPUT
from master.T_EVRL_RULE                      import T_EVRL_RULE
from master.T_EVRL_EVENT_REASSESSMENT        import T_EVRL_EVENT_REASSESSMENT

DF_TEST_EQ  = '0' # =
DF_TEST_NE  = '1' # !=
DF_OPE_OR   = '0' # OR
DF_OPE_AND  = '1' # AND
def TraceLog(msg):
    print("[Trace]" + str(msg))

def DebugLog(msg):
    ##print("[Debug]" + str(msg))
    pass
def ErrorLog(msg):
    print("[Error]" + str(msg))

class Judgement:
    def __init__(self, DBObj, LbIObj, LbCObj, FilterObj, EventObj, FetchedTimeStr, RaccEventObj):
        self.DBObj = DBObj
        self.LbIObj = LbIObj
        self.LbCObj = LbCObj
        self.FilterObj = FilterObj
        self.EventObj  = EventObj
        self.RaccEventObj = RaccEventObj
        self.FetchedTime = {"RuleName": "_exastro_fetched_time", "RuleValue": FetchedTimeStr, "RuleCondition": "0"}

    def RuleJuge(self, RuleRow, UseEveventIdList):
        print(RuleRow['REEVALUATE_TTL'])
        ConditionsList = RuleRow["RULE_CONDITION_JSON"]
        TraceLog("====================================================================================================")
        TraceLog("ルール判定開始 RULE_ID:%s RULE_NAME:%s JSON:%s" % (RuleRow['RULE_ID'], RuleRow['RULE_NAME'], ConditionsList))
        TraceLog("====================================================================================================")

        # グループのフィルタ条件判定用辞書初期化
        GroupResultDict = {}
        GroupResultDict['True'] = 0
        GroupResultDict['False'] = 0
        GroupResultDict['Count'] = 0
        GroupResultDict['Operator'] = ''
        for ConditionRow in ConditionsList:
            GroupOperator = str(ConditionRow['operator'])
            GroupResultDict['Operator'] = GroupOperator
           
            # グループ間の論理演算子「operator」設定確認
            if self.checkOperatorId(GroupOperator) is False:
                ErrorLog("ルール管理　グループ間の論理演算子「operator」が不正 RULE_ID:%s RULE_NAME:%s Json:%s" % (RuleRow['RULE_ID'], RuleRow['RULE_NAME'], str(ConditionsList)))
                return False
            if GroupResultDict['Count'] != 0:
                if not GroupOperator:
                    ErrorLog("ルール管理　グループ間の論理演算子「operator」 未設定 RULE_ID:%s RULE_NAME:%s Json:%s" % (RuleRow['RULE_ID'], RuleRow['RULE_NAME'], str(ConditionsList)))
            
                    return False

            GroupList = ConditionRow['group']
            # グループ毎のループ
            for GroupRow in GroupList:
                RuleOperator = str(GroupRow['operator'])
                # グループの論理演算子「operator」設定確認
                if self.checkOperatorId(RuleOperator) is False:
                    ErrorLog("ルール管理　グループ内の論理演算子「operator」が不正 RULE_ID:%s RULE_NAME:%s Json:%s" % (RuleRow['RULE_ID'], RuleRow['RULE_NAME'], str(ConditionsList)))
                    return False

                if len(GroupRow['filter_key']) == 1:
                    if RuleOperator:
                        ErrorLog("ルール管理　グループ内の論理演算子「operator」が不正 RULE_ID:%s RULE_NAME:%s Json:%s" % (RuleRow['RULE_ID'], RuleRow['RULE_NAME'], str(ConditionsList)))
                        return False
                else:
                    if not RuleOperator:
                        ErrorLog("ルール管理　グループ内の論理演算子「operator」 未設定 RULE_ID:%s RULE_NAME:%s Json:%s" % (RuleRow['RULE_ID'], RuleRow['RULE_NAME'], str(ConditionsList)))
                        return False
            
                # グループ内のフィルタ条件判定用辞書初期化
                FilterResultDict = {}
                FilterResultDict['True'] = 0
                FilterResultDict['False'] = 0
                FilterResultDict['Count'] = 0
                FilterResultDict['Operator'] = RuleOperator
                for FiletrKey in GroupRow['filter_key']:
                    TraceLog("フィルタ管理　判定開始  FILTER_ID: %s" % (FiletrKey))
                    ret, EventIdList = self.FilterJuge(FiletrKey)
                    FilterResultDict['Count'] += 1
                    # フィルター判定 結果退避
                    FilterResultDict[str(ret)] += 1
                    # フィルター判定に使用したイベントID退避
                    if ret is True:
                        TraceLog("フィルタ管理　判定　マッチ  FILTER_ID: %s" % (FiletrKey))
                        for EventId in EventIdList:
                            if UseEveventIdList.count(EventId) == 0:
                                UseEveventIdList.append(EventId)
                    else:
                        TraceLog("フィルタ管理　判定　アンマッチ  FILTER_ID: %s" % (FiletrKey))
                ret = self.checkFilterCondition(FilterResultDict)
                TraceLog("ルール管理　グループ内フィルタ判定結果 %s" % (str(ret)))

                GroupResultDict['Count'] += 1
                GroupResultDict[str(ret)] += 1
        ret = self.checkFilterCondition(GroupResultDict)
        TraceLog("ルール管理　グループ間フィルタ判定結果 %s" % (str(ret)))
        if ret is False:
            return False
        return True

    def checkFilterCondition(self, FilterResultDict):
        if FilterResultDict['Operator'] == DF_OPE_OR:
            if FilterResultDict['True'] != 0:
                return True
        elif FilterResultDict['Operator'] == DF_OPE_AND:
            if FilterResultDict['False'] == 0:
                return True
        # 条件が1個の場合
        else:
            if FilterResultDict['True'] != 0:
                return True
        return False
 
    def checkOperatorId(self, Operator):
        if not Operator:
            return True
        if Operator in (DF_OPE_OR, DF_OPE_AND):
            return True
        return False
          
    def FilterJuge(self, FiletrKey):
        EventKey = ""
        UseEveventIdList = []
        # フィルタ管理から該当情報取得
        FilterRow =  self.FilterObj.findT_EVRL_FILTER(FiletrKey)
        if FilterRow is False:
            ErrorLog("フィルタ管理に該当データ未登録 FILTER_ID:%s" % (FiletrKey))
            return False, UseEveventIdList

        ConditionsList = FilterRow["FILTER_CONDITION_JSON"]
        ConditionsList = json.loads(ConditionsList)

        # グループのフィルタ条件判定用辞書初期化
        GroupResultDict = {}
        GroupResultDict['True'] = 0
        GroupResultDict['False'] = 0
        GroupResultDict['Count'] = 0
        GroupResultDict['Operator'] = ''

        DebugLog(ConditionsList)
        for ConditionRow in ConditionsList:
            GroupOperator = str(ConditionRow['operator'])
            DebugLog("<<GroupOperator: %s>>" % (GroupOperator))

            # グループ間の論理演算子「operator」設定確認
            if self.checkOperatorId(GroupOperator) is False:
                ErrorLog("フィルタ管理　グループ間の論理演算子「operator」が不正 FILTER_ID:%s FILTER_NAME:%s Json:%s" % (FilterRow['FILTER_ID'], FilterRow['FILTER_NAME'], str(ConditionsList)))
                return False, UseEveventIdList

            if GroupResultDict['Count'] != 0:
                if not GroupOperator:
                    ErrorLog("フィルタ管理  グループ間の論理演算子「operator」未設定 FILTER_ID:%s FILTER_NAME:%s Json:%s" % (FilterRow['FILTER_ID'], FilterRow['FILTER_NAME'], str(ConditionsList)))
                    return False, UseEveventIdList

            DebugLog("<<GroupOperator: %s>>" % (GroupOperator))
            GroupList = ConditionRow['group']
            # グループ毎のループ
            for GroupRow in GroupList:
                FilterOperator = str(GroupRow['operator'])
                DebugLog("<<FilterOperator: %s>>" % (FilterOperator))
                FilterOperator = str(GroupRow['operator'])
                # グループの論理演算子「operator」設定確認
                if self.checkOperatorId(FilterOperator) is False:
                    ErrorLog("フィルタ管理　グループ内の論理演算子「operator」が不正 FILTER_ID:%s FILTER_NAME:%s Json:%s" % (FilterRow['FILTER_ID'], FilterRow['FILTER_NAME'], str(ConditionsList)))
                    return False, UseEveventIdList

                if len(GroupRow['rules']) == 1:
                    if FilterOperator:
                        ErrorLog("フィルタ管理　グループ内の論理演算子「operator」が不正 FILTER_ID:%s FILTER_NAME:%s Json:%s" % (FilterRow['FILTER_ID'], FilterRow['FILTER_NAME'], str(ConditionsList)))
                        return False, UseEveventIdList
                else:
                    if not FilterOperator:
                        ErrorLog("フィルタ管理　グループ内の論理演算子「operator」 未設定 FILTER_ID:%s FILTER_NAME:%s Json:%s" % (FilterRow['FILTER_ID'], FilterRow['FILTER_NAME'], str(ConditionsList)))
                        return False, UseEveventIdList

                # グループ内のフィルタ条件判定用辞書初期化
                FilterResultDict = {}
                FilterResultDict['True'] = 0
                FilterResultDict['False'] = 0
                FilterResultDict['Count'] = 0
                FilterResultDict['Operator'] = FilterOperator

                # フィルター毎のループ
                for LabelRow in GroupRow['rules']:
                    EventJudgList = []
                    LabelKey =  str(LabelRow['key'])
                    LabelValue = str(LabelRow['value'])
                    LabelCondition = str(LabelRow['condition'])
                    DebugLog("<<LabelKey: %s>>" % (LabelKey))
                    DebugLog("<<LabelValue: %s>>" % (LabelValue))
                    DebugLog("<<LabelCondition: %s>>" % (LabelCondition))
                    # ルールキーからルールラベル名を取得
                    LabelName = self.LbIObj.getIDtoName(LabelKey)

                    # ラベリングされたイベントからデータを抜出す条件設定
                    EventJudgList.append({"LabelKey": LabelName, "LabelValue": LabelValue, "LabelCondition": LabelCondition})

                    for OptionRow in LabelRow['options']:
                        OptionKey = str(OptionRow['key'])
                        OptionValue = str(OptionRow['value'])
                        OptionCondition = str(OptionRow['condition'])
                        DebugLog("<<OptionKey: %s>>" % (OptionKey))
                        DebugLog("<<OptionValue: %s>>" % (OptionValue))
                        DebugLog("<<OptionCondition: %s>>" % (OptionCondition))
                        # ルールキーからルールラベル名を取得
                        OptionName = self.LbIObj.getIDtoName(OptionKey)
                        # ラベリングされたイベントからデータを抜出す条件設定
                        EventJudgList.append({"LabelKey": OptionName, "LabelValue": OptionValue, "LabelCondition": OptionCondition})

                    TraceLog("フィルタ管理　判定開始  FILTER_ID: %s LABEL_ID: %s" % (FiletrKey, LabelKey))
                    DebugLog(LabelKey)
                    DebugLog(EventJudgList)
                    DebugLog(self.FetchedTime)
                    ret ,EventIdList = self.EventJuge(LabelKey, EventJudgList, self.FetchedTime)
                    FilterResultDict['Count'] += 1
                    # フィルタ判定 結果退避
                    FilterResultDict[str(ret)] += 1
                    # フィルタ判定に使用したイベントID退避
                    if ret is True:
                        TraceLog("フィルタ管理　判定　マッチ  FILTER_ID: %s LABEL_ID: %s" % (FiletrKey, LabelKey))
                        for EventId in EventIdList:
                            if UseEveventIdList.count(EventId) == 0:
                                UseEveventIdList.append(EventId)
                    else:
                        TraceLog("フィルタ管理　判定　アンマッチ  FILTER_ID: %s LABEL_ID: %s" % (FiletrKey, LabelKey))

                    ret = self.checkFilterCondition(FilterResultDict)
                    TraceLog("フィルタ管理　グループ内フィルタ判定結果 %s" % (str(ret)))

                    GroupResultDict['Count'] += 1
                    GroupResultDict[str(ret)] += 1
            ret = self.checkFilterCondition(GroupResultDict)
            TraceLog("フィルタ管理　グループ間フィルタ判定結果 %s" % (str(ret)))
            if ret is False:
                return False, UseEveventIdList
        return True, UseEveventIdList


    def putRaccEvent(self, EventCollPrgRow, RuleRow, UseEveventIdList):
        conclusion_ids = {}
        labelsDict = json.loads(RuleRow["LABELING_INFORMATION"])
        for key, value in labelsDict.items():
            name = self.LbCObj.getIDtoName(key)
            if name is False:
                ErrorLog("ラベル結論マスタ 未登録 LABEL_KEY_ID: %s" % (key))
                return False
            conclusion_ids[name] = key

        RaccEventDict = {}
## UUID設定

        t1 = int(time.time())
        ttl = int(RuleRow['REEVALUATE_TTL'])
        RaccEventDict["_id"] = "uuid"
        RaccEventDict["labels"] = {}
        RaccEventDict["labels"]["_exastro_event_collection_settings_id"] = ''
        RaccEventDict["labels"]["_exastro_fetched_time"] = t1
        RaccEventDict["labels"]["_exastro_end_time"]     = t1 + ttl
        RaccEventDict["labels"]["_exastro_evaluated"]    = "0"
        RaccEventDict["_exatsro_rule_id"] = {}
        RaccEventDict["_exatsro_rule_id"][RuleRow['RULE_ID']] = RuleRow['RULE_NAME']
        RaccEventDict["_exastro_event_id"] = UseEveventIdList
        RaccEventDict["exastro_label_key_conclusion_ids"] = {}
        RaccEventDict["exastro_label_key_conclusion_ids"] = conclusion_ids
        self.RaccEventObj.putT_EVRL_EVENT_REASSESSMENT(RaccEventDict)
        TraceLog("再評価イベント登録")
        TraceLog(RaccEventDict)

        TraceLog("イベント labels._exastro_evaluated 更新 id:%s" % (str(UseEveventIdList)))
        self.EventObj.setUsedT_EVRL_EVENT(UseEveventIdList)
        return True

## 単体テスト用
##    def FilterJuge(self, FiletrKey):
    def testFilterJuge(self, FiletrKey):
        if FiletrKey == 'f_01':
            return True, [FiletrKey]
        if FiletrKey == 'f_02':
            return True, [FiletrKey]
        if FiletrKey == 'f_03':
            return True, [FiletrKey]
        if FiletrKey == 'f_04':
            return True, [FiletrKey]
        if FiletrKey == 'f_05':
            return True, [FiletrKey]
        if FiletrKey == 'f_06':
            return True, [FiletrKey]
        if FiletrKey == 'f_07':
            return True, [FiletrKey]
        if FiletrKey == 'f_08':
            return True, [FiletrKey]
        if FiletrKey == 'f_09':
            return True, [FiletrKey]
        if FiletrKey == 'f_10':
            return True, [FiletrKey]
        if FiletrKey == 'f_11':
            return True, [FiletrKey]
        if FiletrKey == 'f_12':
            return True, [FiletrKey]
        if FiletrKey == 'f_13':
            return True, [FiletrKey]
        if FiletrKey == 'f_14':
            return True, [FiletrKey]
        if FiletrKey == 'f_15':
            return True, [FiletrKey]
        if FiletrKey == 'f_16':
            return True, [FiletrKey]
        if FiletrKey == 'f_17':
            return True, [FiletrKey]
        if FiletrKey == 'f_18':
            return True, [FiletrKey]
        if FiletrKey == 'f_19':
            return True, [FiletrKey]
        if FiletrKey == 'f_20':
            return True, [FiletrKey]
        if FiletrKey == 'f_21':
            return True, [FiletrKey]
        if FiletrKey == 'f_22':
            return True, [FiletrKey]
        if FiletrKey == 'f_23':
            return True, [FiletrKey]
        if FiletrKey == 'f_24':
            return True, [FiletrKey]
        if FiletrKey == 'f_25':
            return True, [FiletrKey]
        if FiletrKey == 'f_26':
            return True, [FiletrKey]
        if FiletrKey == 'f_27':
            return True, [FiletrKey]
        if FiletrKey == 'f_28':
            return True, [FiletrKey]
        if FiletrKey == 'f_29':
            return True, [FiletrKey]
        if FiletrKey == 'f_30':
            return True, [FiletrKey]
        if FiletrKey == 'f_31':
            return True, [FiletrKey]
        if FiletrKey == 'f_32':
            return True, [FiletrKey]
        if FiletrKey == 'f_33':
            return True, [FiletrKey]
        if FiletrKey == 'f_34':
            return True, [FiletrKey]
        if FiletrKey == 'f_35':
            return True, [FiletrKey]
        if FiletrKey == 'f_36':
            return True, [FiletrKey]
        if FiletrKey == 'f_37':
            return True, [FiletrKey]
        if FiletrKey == 'f_38':
            return True, [FiletrKey]
        if FiletrKey == 'f_39':
            return True, [FiletrKey]
        if FiletrKey == 'f_40':
            return True, [FiletrKey]
        if FiletrKey == 'f_41':
            return True, [FiletrKey]
        if FiletrKey == 'f_42':
            return True, [FiletrKey]
        if FiletrKey == 'f_43':
            return True, [FiletrKey]
        if FiletrKey == 'f_44':
            return True, [FiletrKey]
        if FiletrKey == 'f_45':
            return True, [FiletrKey]
        if FiletrKey == 'f_46':
            return True, [FiletrKey]
        if FiletrKey == 'f_47':
            return True, [FiletrKey]
        if FiletrKey == 'f_48':
            return True, [FiletrKey]
        if FiletrKey == 'f_49':
            return True, [FiletrKey]
        if FiletrKey == 'f_50':
            return True, [FiletrKey]
        if FiletrKey == 'f_51':
            return True, [FiletrKey]
        if FiletrKey == 'f_52':
            return True, [FiletrKey]
        if FiletrKey == 'f_53':
            return True, [FiletrKey]
        if FiletrKey == 'f_54':
            return True, [FiletrKey]
        if FiletrKey == 'f_55':
            return True, [FiletrKey]
        if FiletrKey == 'f_56':
            return True, [FiletrKey]
        if FiletrKey == 'f_57':
            return True, [FiletrKey]
        if FiletrKey == 'f_58':
            return True, [FiletrKey]
        if FiletrKey == 'f_59':
            return True, [FiletrKey]
        if FiletrKey == 'f_60':
            return True, [FiletrKey]

## 単体テスト用
    def EventJuge(self, FilterKey, EventJudgList, FetchedTime):
        if FilterKey == 'i_01':
            return True, ['e_01']
        if FilterKey == 'i_02':
            return True, ['e_02']
        if FilterKey == 'i_03':
            return True, ['e_03']
        if FilterKey == 'i_04':
            return True, ['e_04']
        if FilterKey == 'i_05':
            return True, ['e_05']
        if FilterKey == 'i_06':
            return True, ['e_06']
        if FilterKey == 'i_07':
            return True, ['e_07']
        if FilterKey == 'i_08':
            return True, ['e_08']
        if FilterKey == 'i_09':
            return True, ['e_09']
        if FilterKey == 'i_10':
            return True, ['e_10']
        if FilterKey == 'i_11':
            return True, ['e_11']
        if FilterKey == 'i_12':
            return True, ['e_12']
        if FilterKey == 'i_13':
            return True, ['e_13']
        if FilterKey == 'i_14':
            return True, ['e_14']
        if FilterKey == 'i_15':
            return True, ['e_15']
        if FilterKey == 'i_16':
            return True, ['e_16']
        if FilterKey == 'i_17':
            return True, ['e_17']
        if FilterKey == 'i_18':
            return True, ['e_18']
        if FilterKey == 'i_19':
            return True, ['e_19']
        if FilterKey == 'i_20':
            return True, ['e_20']
        if FilterKey == 'i_21':
            return True, ['e_21']
        if FilterKey == 'i_22':
            return True, ['e_22']
        if FilterKey == 'i_23':
            return True, ['e_23']
        if FilterKey == 'i_24':
            return True, ['e_24']
        if FilterKey == 'i_25':
            return True, ['e_25']
        if FilterKey == 'i_26':
            return True, ['e_26']
        if FilterKey == 'i_27':
            return True, ['e_27']
        if FilterKey == 'i_28':
            return True, ['e_28']
        if FilterKey == 'i_29':
            return True, ['e_29']
        if FilterKey == 'i_30':
            return True, ['e_30']
        if FilterKey == 'i_31':
            return True, ['e_31']
        if FilterKey == 'i_32':
            return True, ['e_32']
        if FilterKey == 'i_33':
            return True, ['e_33']
        if FilterKey == 'i_34':
            return True, ['e_34']
        if FilterKey == 'i_35':
            return True, ['e_35']
        if FilterKey == 'i_36':
            return True, ['e_36']
        if FilterKey == 'i_37':
            return True, ['e_37']
        if FilterKey == 'i_38':
            return True, ['e_38']
        if FilterKey == 'i_39':
            return True, ['e_39']
        if FilterKey == 'i_40':
            return True, ['e_40']
        if FilterKey == 'i_41':
            return True, ['e_41']
        if FilterKey == 'i_42':
            return True, ['e_42']
        if FilterKey == 'i_43':
            return True, ['e_43']
        if FilterKey == 'i_44':
            return True, ['e_44']
        if FilterKey == 'i_45':
            return True, ['e_45']
        if FilterKey == 'i_46':
            return True, ['e_46']
        if FilterKey == 'i_47':
            return True, ['e_47']
        if FilterKey == 'i_48':
            return True, ['e_48']
        if FilterKey == 'i_49':
            return True, ['e_49']
        if FilterKey == 'i_50':
            return True, ['e_50']
        if FilterKey == 'i_51':
            return True, ['e_51']
        if FilterKey == 'i_52':
            return True, ['e_52']
        if FilterKey == 'i_53':
            return True, ['e_53']
        if FilterKey == 'i_54':
            return True, ['e_54']
        if FilterKey == 'i_55':
            return True, ['e_55']
        if FilterKey == 'i_56':
            return True, ['e_56']
        if FilterKey == 'i_57':
            return True, ['e_57']
        if FilterKey == 'i_58':
            return True, ['e_58']
        if FilterKey == 'i_59':
            return True, ['e_59']
        if FilterKey == 'i_60':
            return True, ['e_60']
        if FilterKey == 'i_61':
            return True, ['e_61']
        if FilterKey == 'i_62':
            return True, ['e_62']
        if FilterKey == 'i_63':
            return True, ['e_63']
        if FilterKey == 'i_64':
            return True, ['e_64']
        if FilterKey == 'i_65':
            return True, ['e_65']
        if FilterKey == 'i_66':
            return True, ['e_66']
        if FilterKey == 'i_67':
            return True, ['e_67']
        if FilterKey == 'i_68':
            return True, ['e_68']
        if FilterKey == 'i_69':
            return True, ['e_69']
        if FilterKey == 'i_70':
            return True, ['e_70']
        if FilterKey == 'i_71':
            return True, ['e_71']
        if FilterKey == 'i_72':
            return True, ['e_72']
        if FilterKey == 'i_73':
            return True, ['e_73']
        if FilterKey == 'i_74':
            return True, ['e_74']
        if FilterKey == 'i_75':
            return True, ['e_75']
        if FilterKey == 'i_76':
            return True, ['e_76']
        if FilterKey == 'i_77':
            return True, ['e_77']
        if FilterKey == 'i_78':
            return True, ['e_78']
        if FilterKey == 'i_79':
            return True, ['e_79']
        if FilterKey == 'i_80':
            return True, ['e_80']
        if FilterKey == 'i_81':
            return True, ['e_81']
        if FilterKey == 'i_82':
            return True, ['e_82']
        if FilterKey == 'i_83':
            return True, ['e_83']
        if FilterKey == 'i_84':
            return True, ['e_84']
        if FilterKey == 'i_85':
            return True, ['e_85']
        if FilterKey == 'i_86':
            return True, ['e_86']
        if FilterKey == 'i_87':
            return True, ['e_87']
        if FilterKey == 'i_88':
            return True, ['e_88']
        if FilterKey == 'i_89':
            return True, ['e_89']
        if FilterKey == 'i_90':
            return True, ['e_90']
        if FilterKey == 'i_91':
            return True, ['e_91']
        if FilterKey == 'i_92':
            return True, ['e_92']
        if FilterKey == 'i_93':
            return True, ['e_93']
        if FilterKey == 'i_94':
            return True, ['e_94']
        if FilterKey == 'i_95':
            return True, ['e_95']
        if FilterKey == 'i_96':
            return True, ['e_96']
        if FilterKey == 'i_97':
            return True, ['e_97']
        if FilterKey == 'i_98':
            return True, ['e_98']
        if FilterKey == 'i_99':
            return True, ['e_99']
        if FilterKey == 'i_200':
            return True, ['e_200']
        if FilterKey == 'i_201':
            return True, ['e_201']


def JugeMain(DBObj, EventCollPrgList):
    # ラベルマスタ取得
    DebugLog("ラベルマスタ取得")
    LbIObj = T_EVRL_LABEL_KEY_INPUT(DBObj, 'csv/T_EVRL_LABEL_KEY_INPUT.csv')

    # 結論ラベルマスタ取得
    DebugLog("結論ラベルマスタ取得")
    LbCObj = T_EVRL_LABEL_KEY_CONCLUSION(DBObj, 'csv/T_EVRL_LABEL_KEY_CONCLUSION.csv')

    # ファルタ管理取得
    DebugLog("ファルタ管理取得")
    FilterObj = T_EVRL_FILTER(DBObj, 'csv/T_EVRL_FILTER.csv')

    # ルール管理取得
    DebugLog("ルール管理取得")
    RuleObj = T_EVRL_RULE(DBObj, 'csv/T_EVRL_RULE.csv')
    RuleList = RuleObj.getT_EVRL_RULE()
    if len(RuleList) == 0:
        DebugLog("処理対象レコードなし。Table:T_EVRL_RULE")
        return False

    # イベント取得
    EventObj = T_EVRL_EVENT(DBObj, 'csv/T_EVRL_EVENT.csv')
    EventList = EventObj.getT_EVRL_EVENT()
    
    # イベント収集経過時間取得
    EventCollPrgRow = EventCollPrgList[0]
    FetchedTimeStr = str(EventCollPrgRow['FETCHED_TIME'])
    DebugLog("FETCHED_TIME:%s" % (FetchedTimeStr))
    
    # 再評価イベント登録
    RaccEventObj = T_EVRL_EVENT_REASSESSMENT(DBObj)
    
    JugeObj = Judgement(DBObj, LbIObj, LbCObj, FilterObj, EventObj, FetchedTimeStr, RaccEventObj)
    RuleJudgInfoList = []
    for RuleRow in RuleList:
        # ルール判定
        RuleRow["RULE_CONDITION_JSON"] = json.loads(RuleRow["RULE_CONDITION_JSON"])
        UseEveventIdList = []
        ret = JugeObj.RuleJuge(RuleRow, UseEveventIdList)
        if ret is True:
            TraceLog("ルール判定 マッチ")
            JugeObj.putRaccEvent(EventCollPrgRow, RuleRow, UseEveventIdList)
        else:
            TraceLog("ルール判定 アンマッチ")
            sys.exit(1)


###################################
def main():
    DBObj = "DB"
    # イベント収集経過より未処理レコード取得
    DebugLog("イベント収集経過より未処理レコード取得")

    EventCollPrgObj = T_EVRL_EVENT_COLLECTION_PROGRESS(DBObj)
    EventCollPrgList = EventCollPrgObj.getT_EVRL_EVENT_COLLECTION_PROGRESS()
    if len(EventCollPrgList) == 0:
        DebugLog("処理対象レコードなし。Table:T_EVRL_EVENT_COLLECTION_PROGRESS")
        return False

    DebugLog("ルール判定開始")
    ret = JugeMain(DBObj,EventCollPrgList)
    if ret is False:
        DebugLog("ルール判定異常")
    
    DebugLog("ルール判定完了")


    DebugLog("イベント収集経過更新")
    ret = EventCollPrgObj.setUsedT_EVRL_EVENT_COLLECTION_PROGRESS(EventCollPrgList)

main()
