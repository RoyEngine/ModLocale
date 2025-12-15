package second_in_command.misc.backgrounds

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.campaign.FactionSpecAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import exerelin.campaign.backgrounds.BaseCharacterBackground
import exerelin.utilities.NexFactionConfig
import second_in_command.SCUtils
import second_in_command.misc.SCSettings
import second_in_command.misc.randomAndRemove
import second_in_command.specs.SCAptitudeSpec
import second_in_command.specs.SCBaseAptitudePlugin
import second_in_command.specs.SCSpecStore


class AssociatesBackground : BaseCharacterBackground() {

    override fun getShortDescription(factionSpec: FactionSpecAPI?, factionConfig: NexFactionConfig?): String {
        return "你命中注定与几位各具特色的亲友一同体验这段星空之旅，他们每个人都对舰队运作有属于自己的独到理解。"
    }

    override fun getLongDescription(factionSpec: FactionSpecAPI?, factionConfig: NexFactionConfig?): String {
        return "与你结伴同行的伙伴们对你的舰队有着种种影响，没有他们你将一事无成，" +
                "你也绝对不会和他们中的任何一个断绝关系，尽管要设法有效协调并适应他们的长处绝非易事。"
    }

    fun getTooltip(tooltip: TooltipMakerAPI) {

        tooltip.addSpacer(10f)

        var hc = Misc.getHighlightColor()
        var nc = Misc.getNegativeHighlightColor()

        var text = "只有能够作为初始选项的天赋才会被随机选择。"
        if (SCSettings.unrestrictedAssociates!!) text = ""

        var label = tooltip.addPara(
                    "游戏开始时，你将会{随机获得 3 位}天赋各异的{执行军官}。你无法通过任何手段{将其更换或解雇}。 $text\n\n" +
	"你们昔日同行的经历使你们在 \"战斗\" 天赋上获得 1 额外技能点}。 由于执行军官的特殊性，他们的经验获取减少 30% 。\n\n" +
                    "{不建议第一次尝试 \"舰队副官\" 模组的玩家尝试该出身背景}。", 0f)

        label.setHighlight("随机获得 3 位", "执行军官", "将其更换或解雇", "战斗", "额外技能点", "30%", "不建议第一次尝试 \"舰队副官\" 模组的玩家尝试该出身背景" )
        label.setHighlightColors(hc, nc, hc, hc, nc, nc)

    }



    override fun addTooltipForSelection(tooltip: TooltipMakerAPI?, factionSpec: FactionSpecAPI?, factionConfig: NexFactionConfig?, expanded: Boolean) {
        super.addTooltipForSelection(tooltip, factionSpec, factionConfig, expanded)
        getTooltip(tooltip!!)
    }

    override fun addTooltipForIntel(tooltip: TooltipMakerAPI?, factionSpec: FactionSpecAPI?, factionConfig: NexFactionConfig?) {
        super.addTooltipForIntel(tooltip, factionSpec, factionConfig)
        getTooltip(tooltip!!)
    }

    override fun onNewGameAfterTimePass(factionSpec: FactionSpecAPI?, factionConfig: NexFactionConfig?) {
        var data = SCUtils.getPlayerData()

        var aptitudes = SCSpecStore.getAptitudeSpecs().map { it.getPlugin() }.filter { !it.tags.contains("restricted") }.toMutableList()
        if (!SCSettings.unrestrictedAssociates!!) {
            aptitudes = aptitudes.filter { it.tags.contains("startingOption") }.toMutableList() //Only pick aptitudes available from the starting interaction
        }

        var picks = ArrayList<SCBaseAptitudePlugin>()

        for (i in 0 until 3) {
            var pick = aptitudes.randomAndRemove()
            var categories = pick.categories

            //Remove aptitudes that share a category with this one
            for (cat in categories) {
                aptitudes = aptitudes.filter { it.categories.none { it == cat } }.toMutableList()
            }

            picks.add(pick)
        }

        for (pick in picks) {
            var officer = SCUtils.createRandomSCOfficer(pick.id)

            officer.person.memoryWithoutUpdate.set("\$sc_associatesOfficer", true)

            data.addOfficerToFleet(officer);
            data.setOfficerInEmptySlotIfAvailable(officer, true)
        }

        Global.getSector().characterData.person.stats.points += 1

        Global.getSector().memoryWithoutUpdate.set("\$sc_selectedStart", true) //Prevent Initial Hiring Dialog from showing up

        fillMissingSlot()
    }


    companion object {
        //Called if you have an associates run with 4XOs active
        fun fillMissingSlot() {
            var data = SCUtils.getPlayerData()

            if (!SCUtils.isAssociatesBackgroundActive()) return
            //if (!SCSettings.enable4thSlot) return
            var max = 3
            if (SCSettings.enable4thSlot) max = 4
            if (data.getAssignedOfficers().filterNotNull().size >= max) return

            var aptitudes = SCSpecStore.getAptitudeSpecs().map { it.getPlugin() }.filter { !it.tags.contains("restricted") }.toMutableList()
            if (!SCSettings.unrestrictedAssociates!!) {
                aptitudes = aptitudes.filter { it.tags.contains("startingOption") }.toMutableList() //Only pick aptitudes available from the starting interaction
            }

            aptitudes = aptitudes.filter { !data.hasAptitudeInFleet(it.id) }.toMutableList()

            var picks = ArrayList<SCBaseAptitudePlugin>()

            for (aptitude in aptitudes) {

                var valid = true

                for (category in aptitude.categories) {
                    for (active in data.getActiveOfficers()) {
                        if (active.getAptitudePlugin().categories.contains(category)) {
                            valid = false
                        }
                    }
                }
                if (valid) picks.add(aptitude)
            }

            var pick = picks.randomOrNull() ?: return

            var officer = SCUtils.createRandomSCOfficer(pick.id)
            officer.person.memoryWithoutUpdate.set("\$sc_associatesOfficer", true)

            data.addOfficerToFleet(officer);
            data.setOfficerInEmptySlotIfAvailable(officer, true)
        }
    }






}