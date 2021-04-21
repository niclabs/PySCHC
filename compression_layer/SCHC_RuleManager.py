class SCHC_RuleManager:
    RULE_ID_NOT_COMPRESSED = 250

    def __init__(self):
        self.context = []
        self.MatchingOperators = {
            "ignore": self.mo_ignore,
            "equal": self.mo_equal,
            "match-mapping": self.mo_matchmapping,
            "MSB": self.mo_msb
        }

    def mo_ignore(self, length, fv, tv, cda):
        return True

    def mo_equal(self, length, fv, tv, cda):
        return fv == tv

    def mo_matchmapping(self, length, fv, tv, cda):
        if type(tv) is dict:
            for mappingID, mappingValue in tv.items():
                if mappingValue == fv:
                    return True
            return False
        elif type(tv) is list:
            for mappingValue in tv:
                # print ('\t', type (mappingValue), '  <=> ', type (FV), end='|')
                # print ('\t', mappingValue, '  <=> ', FV)
                if type(mappingValue) != type(fv):
                    return False
                if mappingValue == fv:
                    return True
            return False
        else:
            return False

    # Only accepts length in bits
    def mo_msb(self, length, fv, tv, cda, n_bits):
        return (fv>>(length - n_bits) ^ tv) == 0

    def get_rule_from_id(self, rule_id):
        for r in self.context:
            if r["ruleid"] == rule_id:
                return r
        print("Rule not found")
        return False

    def add_rule(self, rule):
        """Add a rule to the context, ruleid must be unique """
        added_rule_id = rule["ruleid"]
        for r in self.context:
            if r["ruleid"] == added_rule_id:
                raise ValueError('Rule ID already exists ', added_rule_id)

        self.context.append(rule)

    def find_rule_from_headers(self, headers, direction):

        headers_keys = headers.keys()
        for rule in self.context:
            # If a header of the current packet is not in the FIDs of the rule, the rule MUST be discarded
            flag = False
            for header in headers_keys:
                coincidence = False
                for content in rule["content"]:
                    if header[0] == content[0]:
                        coincidence = True
                        break
                if coincidence is False:
                    print("Header \"" + header[0] + "\" not found in Rule ID: " + str(rule["ruleid"]))
                    print("The Rule MUST be disregarded")
                    flag = True
                    break
            if flag:
                continue

            # If an FID of the rule is not in the set of headers of the current packet, the rule MUST be discarded
            flag = False
            for content in rule["content"]:
                coincidence = False
                for header in headers_keys:
                    if header[0] == content[0]:
                        coincidence = True
                        break
                if coincidence is False:
                    print("Field ID \"" + content[0] + "\" of the Rule " + str(rule["ruleid"]) + "not found in "
                                                                                                 "Headers List")
                    print("The Rule MUST be disregarded")
                    flag = True
                    break
            if flag:
                continue

            # If a pair (header, direction) of the current packet is not in the rule, the rule MUST be discarded
            flag = False
            for header in headers_keys:
                coincidence = False
                for content in rule["content"]:
                    DI = content[3]
                    if header[0] == content[0] and (direction is DI or DI is "Bi"):
                        coincidence = True
                        break
                if coincidence is False:
                    print("Header \"" + header[0] + "\" does not match with FID and DI in the RuleID " +
                          str(rule["ruleid"]))
                    print("The Rule MUST be disregarded")
                    flag = True
                    break
            if flag:
                continue

            # If a tuple (header, direction, position) of the current packet is not in the rule, the rule MUST be discarded
            flag = False
            for header in headers_keys:
                coincidence = False
                for content in rule["content"]:
                    PO = content[2]
                    DI = content[3]
                    if header[0] == content[0] and (direction is DI or DI is "Bi") and (header[1] is PO):
                        coincidence = True
                        break
                if coincidence is False:
                    print("Header \"" + header[0] + "\" does not match with FID, DI and FP in the RuleID " +
                          str(rule["ruleid"]))
                    print("The Rule MUST be disregarded")
                    flag = True
                    break
            if flag:
                continue

            # After associating each header value with a (FID, DI, FP) tuple, the matching operators (MO) are applied
            # with the target value (TV) and the header value.
            # If at least one MO returns false, the rule MUST be discarded
            # Looking MO
            MO_is_false = False
            for header in headers_keys:
                for content in rule["content"]:
                    # FID = content[0]
                    LENGTH = content[1]
                    PO = content[2]
                    DI = content[3]
                    if header[0] == content[0] and (direction is DI or DI is "Bi") and (header[1] is PO):
                        FV = headers.get(header)[0]
                        TV = content[4]
                        MO = content[5]
                        CDA = content[6]
                        if MO[:3] == "MSB":
                            if not self.MatchingOperators.get("MSB")(LENGTH, FV, TV, CDA, int(MO[4:-1])):
                                MO_is_false = True
                                break
                        elif not self.MatchingOperators.get(MO)(LENGTH, FV, TV, CDA):
                            MO_is_false = True
                            break

            if MO_is_false:
                continue
            else:
                return rule["ruleid"]

        return self.RULE_ID_NOT_COMPRESSED
